"""C12 local Perceval comparison with a separate creation-operator oracle.

The oracle uses only Python math; Perceval is imported lazily for actual SDK runs.
All SDK validation observations concern the recorded Python optimization mode.
"""
import argparse
import cmath
import importlib.metadata
import itertools
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

TOLERANCE = 1e-10
PROBES = ('component_index', 'input_dimension', 'negative_occupation',
          'nonunitary', 'three_photons', 'loss_component')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def occupations(modes=3, photons=2):
    return [x for x in itertools.product(range(photons+1), repeat=modes) if sum(x)==photons]


def identity(modes):
    return [[complex(i==j) for j in range(modes)] for i in range(modes)]


def multiply(left, right):
    modes=len(left)
    return [[sum(left[i][k]*right[k][j] for k in range(modes))
             for j in range(modes)] for i in range(modes)]


def rotation(offset, angle):
    result=identity(3)
    c,s=math.cos(angle),math.sin(angle)
    result[offset][offset]=result[offset+1][offset+1]=c
    result[offset][offset+1]=-s
    result[offset+1][offset]=s
    return result


def oracle_unitary(a,b,c,phi):
    phase=identity(3);phase[1][1]=cmath.exp(1j*phi)
    return multiply(rotation(0,c),multiply(rotation(1,b),multiply(phase,rotation(0,a))))


def bosonic_probabilities(unitary, incoming):
    """Apply transformed creation operators to normalized Fock input.

    This is neither a permanent call nor Perceval's SLOS implementation.
    Complex floating arithmetic represents the full finite Fock space.
    """
    modes=len(incoming)
    amplitudes={(0,)*modes:1+0j}
    for source,count in enumerate(incoming):
        for unused in range(count):
            following={}
            for state,amplitude in amplitudes.items():
                for target in range(modes):
                    new=list(state);new[target]+=1;new=tuple(new)
                    following[new]=following.get(new,0j)+amplitude*unitary[target][source]*math.sqrt(state[target]+1)
            amplitudes=following
    factor=math.prod(math.factorial(count) for count in incoming)
    return {state:abs(amplitude)**2/factor for state,amplitude in amplitudes.items()}


def validate_request(request):
    """Explicit experiment boundary, independent of optional SDK asserts."""
    require(type(request) is dict and set(request)=={'modes','input','angles','loss','noise','observable'},'request fields')
    require(type(request['modes']) is int and request['modes']==3,'exactly3modes')
    incoming=request['input']
    require(type(incoming) is list and len(incoming)==3,'input dimension')
    require(all(type(x) is int and x>=0 for x in incoming),'nonnegative integer occupations')
    require(sum(incoming)==2,'exactly2photons')
    angles=request['angles']
    require(type(angles) is list and len(angles)==4,'four angles')
    require(all(type(x) in (int,float) and math.isfinite(x) for x in angles),'finite angles in radians')
    require(type(request['loss']) in (int,float) and request['loss']==0,'loss unsupported')
    require(request['noise'] is False,'noise unsupported')
    require(request['observable']=='photon_number_resolving_distribution','observable unsupported')
    return request


def import_sdk():
    os.environ.setdefault('MPLBACKEND','Agg')
    os.environ.setdefault('MPLCONFIGDIR','/tmp/quantage-c12-matplotlib')
    import perceval as pcvl
    return pcvl


def make_circuit(pcvl,a,b,c,phi):
    return (pcvl.Circuit(3).add(0,pcvl.BS.Ry(theta=2*a))
            .add(1,pcvl.PS(phi)).add(1,pcvl.BS.Ry(theta=2*b))
            .add(0,pcvl.BS.Ry(theta=2*c)))


def probe(name):
    pcvl=import_sdk();phase='construction'
    try:
        circuit=pcvl.Circuit(3);incoming=[1,1,0]
        if name=='component_index':circuit.add(2,pcvl.BS.Ry())
        elif name=='input_dimension':incoming=[1,1]
        elif name=='negative_occupation':incoming=[3,-1,0]
        elif name=='nonunitary':
            circuit.add(0,pcvl.Unitary(pcvl.Matrix([[1,0,0],[0,0.9,0],[0,0,1]])))
        elif name=='three_photons':incoming=[1,1,1]
        elif name=='loss_component':
            if not hasattr(pcvl,'LC'):
                return {'probe':name,'sdk_status':'unsupported_api','reason':'LC not exposed'}
            circuit.add(0,pcvl.LC(0.1))
        else:raise ValueError('unknown probe')
        phase='set_circuit';backend=pcvl.SLOSBackend();backend.set_circuit(circuit)
        phase='set_input_state';backend.set_input_state(pcvl.BasicState(incoming))
        phase='prob_distribution';distribution=backend.prob_distribution()
        return {'probe':name,'sdk_status':'accepted','phase':phase,'probability_sum':sum(float(v) for v in distribution.values()),'states':{str(s):float(v) for s,v in distribution.items()}}
    except Exception as error:
        return {'probe':name,'sdk_status':'rejected','phase':phase,'exception':type(error).__name__,'message':str(error)}


def contract_probes():
    valid={'modes':3,'input':[1,1,0],'angles':[0,0,0,0],'loss':0,'noise':False,'observable':'photon_number_resolving_distribution'}
    data=[('valid',{},True),('dimension',{'input':[1,1]},False),('negative',{'input':[3,-1,0]},False),('three_photons',{'input':[1,1,1]},False),('loss',{'loss':0.1},False),('noise',{'noise':True},False),('boolean',{'input':[True,1,0]},False),('nan',{'angles':[float('nan'),0,0,0]},False),('threshold',{'observable':'threshold_clicks'},False)]
    records=[]
    for name,changes,expected in data:
        candidate={**valid,**changes}
        try:validate_request(candidate);accepted=True;reason=None
        except ValueError as error:accepted=False;reason=str(error)
        records.append({'probe':name,'accepted':accepted,'expected':expected,'reason':reason})
        require(accepted==expected,'contract fixture mismatch '+name)
    return records


def execute(output):
    start=time.perf_counter();cpu=time.process_time();output.mkdir(parents=True,exist_ok=True)
    require(not (output/'raw.jsonl').exists(),'raw output already exists')
    pcvl=import_sdk()
    values=(0,math.pi/4,math.pi/2);phases=(0,math.pi/3,math.pi)
    count=0;max_prob=0;max_unitary=0;max_norm=0;hom=None
    states=occupations();backend_type=None
    with (output/'raw.jsonl').open('x') as raw:
        for a,b,c,phi in itertools.product(values,values,values,phases):
            expected_u=oracle_unitary(a,b,c,phi)
            circuit=make_circuit(pcvl,a,b,c,phi);observed_u=circuit.compute_unitary()
            error_u=max(abs(complex(observed_u[i,j])-expected_u[i][j]) for i in range(3) for j in range(3))
            require(error_u<TOLERANCE,'unitary mismatch')
            # Independent column orthonormality check on our matrix.
            error_unitarity=max(abs(sum(expected_u[k][i].conjugate()*expected_u[k][j] for k in range(3))-(i==j)) for i in range(3) for j in range(3))
            require(error_unitarity<TOLERANCE,'oracle nonunitary')
            max_unitary=max(max_unitary,error_u)
            backend=pcvl.SLOSBackend();backend.set_circuit(circuit)
            backend_type=type(backend).__module__+'.'+type(backend).__name__
            for incoming in states:
                validate_request({'modes':3,'input':list(incoming),'angles':[a,b,c,phi],'loss':0,'noise':False,'observable':'photon_number_resolving_distribution'})
                backend.set_input_state(pcvl.BasicState(list(incoming)))
                distribution=backend.prob_distribution()
                observed={tuple(s):float(p) for s,p in distribution.items()}
                require(all(state in states for state in observed),'SDK photon-number violation')
                expected=bosonic_probabilities(expected_u,incoming)
                rows=[{'output':list(state),'oracle':expected.get(state,0.0),'sdk':observed.get(state,0.0)} for state in states]
                error=max(abs(r['oracle']-r['sdk']) for r in rows)
                norm_error=max(abs(sum(expected.values())-1),abs(sum(observed.values())-1))
                record={'evaluation':count,'angles':{'a':a,'b':b,'c':c,'phi':phi},'input':list(incoming),'probabilities':rows,'max_probability_error':error,'unitary_error':error_u,'normalization_error':norm_error,'status':'passed' if max(error,norm_error)<TOLERANCE and min(observed.values(),default=0)>=-TOLERANCE else 'failed','sdk_accepted':True,'specific_hardware_compatible':'unverified','qpu_executed':False}
                raw.write(json.dumps(record,allow_nan=False)+'\n');raw.flush()
                require(record['status']=='passed','probability/norm mismatch')
                if a==math.pi/4 and b==c==phi==0 and incoming==(1,1,0):
                    hom=record
                    for state,expected_p in [((2,0,0),0.5),((0,2,0),0.5),((1,1,0),0)]:
                        require(abs(observed.get(state,0)-expected_p)<TOLERANCE,'HOM mismatch')
                count+=1;max_prob=max(max_prob,error);max_norm=max(max_norm,norm_error)
    require(count==486 and hom is not None,'grid incomplete or missing HOM')
    probes=[]
    for name in PROBES:
        command=[sys.executable,'-m','quantage.sdk_photon','--probe',name]
        try:
            p=subprocess.run(command,capture_output=True,text=True,timeout=20)
            if p.returncode==0:
                result=json.loads(p.stdout.splitlines()[-1])
            else:result={'probe':name,'sdk_status':'process_error','exit_code':p.returncode}
            result['stderr']=p.stderr;result['command']=command;probes.append(result)
        except subprocess.TimeoutExpired as error:
            probes.append({'probe':name,'sdk_status':'timeout','command':command,'timeout_seconds':20})
    metrics={'evaluations':count,'configurations':81,'output_probabilities_compared':count*6,'max_probability_error':max_prob,'max_unitary_error':max_unitary,'max_normalization_error':max_norm,'tolerance':TOLERANCE,'hom':hom,'sdk_probes':probes,'contract_probes':contract_probes(),'software':{'python':platform.python_version(),**{name:importlib.metadata.version(name) for name in ('perceval-quandela','exqalibur','numpy','scipy','sympy')}},'backend_type':backend_type,'python_optimization':sys.flags.optimize,'elapsed_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,'qpu_jobs':0,'external_purchase_eur':0,'specific_hardware_compatible':'unverified','independence':'distinct implementation oracle by author; independent reviewer pending','randomness':False,'sampling':'fixed complete parameter grid; no natural population or independent samples'}
    (output/'metrics.json').write_text(json.dumps(metrics,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:metrics[k] for k in ('evaluations','output_probabilities_compared','max_probability_error','max_unitary_error','max_normalization_error','elapsed_seconds','backend_type','qpu_jobs')}))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);parser.add_argument('--probe',choices=PROBES)
    args=parser.parse_args()
    if args.probe:print(json.dumps(probe(args.probe),allow_nan=False))
    else:
        if args.output is None:parser.error('--output required')
        execute(args.output)


if __name__=='__main__':main()
