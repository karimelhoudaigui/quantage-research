"""C13 local Pulser ODE versus a separately constructed finite Hamiltonian."""
import argparse
import cmath
import importlib.metadata
import itertools
import json
import math
import os
from pathlib import Path
import platform
import sys
import time
import warnings

STATES=((0,0),(0,1),(1,0),(1,1))  # Excitations, ordered gg,gr,rg,rr.
PROBABILITY_TOLERANCE=0.005
HAMILTONIAN_TOLERANCE=1e-10
NORMALIZATION_TOLERANCE=1e-8


def require(value,message):
    if not value:raise ValueError(message)


def hamiltonian(omega,delta,phase,interaction):
    result=[[0j]*4 for unused in range(4)]
    for source,state in enumerate(STATES):
        result[source][source]=-delta*sum(state)+interaction*state[0]*state[1]
        for atom in range(2):
            target=list(state);target[atom]=1-target[atom]
            index=STATES.index(tuple(target))
            result[index][source]=omega/2*cmath.exp((1j if state[atom]==0 else -1j)*phase)
    return result


def oracle_probabilities(matrix,time_us):
    import numpy as np
    eigenvalues,eigenvectors=np.linalg.eigh(np.array(matrix,dtype=complex))
    initial=np.array([1,0,0,0],dtype=complex)
    final=eigenvectors@(np.exp(-1j*eigenvalues*time_us)*(eigenvectors.conj().T@initial))
    return [float(abs(amplitude)**2) for amplitude in final]


def sdk_imports():
    os.environ.setdefault('MPLBACKEND','Agg')
    os.environ.setdefault('MPLCONFIGDIR','/tmp/quantage-c13-matplotlib')
    import pulser
    from pulser_simulation import QutipEmulator
    return pulser,QutipEmulator


def build(pulser,distance,duration,omega,delta,phase):
    register=pulser.Register({'q0':(-distance/2,0),'q1':(distance/2,0)})
    sequence=pulser.Sequence(register,pulser.AnalogDevice)
    sequence.declare_channel('global','rydberg_global')
    sequence.add(pulser.Pulse.ConstantPulse(duration,omega,delta,phase),'global')
    sequence.measure('ground-rydberg')
    return sequence


def probes(pulser):
    names=('too_close','too_far','missing_channel','over_amplitude','over_detuning','short_duration','clock_duration','long_sequence','missing_layout')
    records=[];device=pulser.AnalogDevice;channel=device.channels['rydberg_global']
    for name in names:
        actual_duration=None
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            try:
                distance=2 if name=='too_close' else 10
                qubits={'q0':(-distance/2,0),'q1':(distance/2,0)}
                if name=='too_far':qubits['q1']=(100,0)
                sequence=pulser.Sequence(pulser.Register(qubits),device)
                sequence.declare_channel('test','rydberg_local' if name=='missing_channel' else 'rydberg_global')
                omega=channel.max_amp*1.1 if name=='over_amplitude' else 1
                delta=channel.max_abs_detuning*1.1 if name=='over_detuning' else 0
                duration=8 if name=='short_duration' else 101 if name=='clock_duration' else 6004 if name=='long_sequence' else 100
                sequence.add(pulser.Pulse.ConstantPulse(duration,omega,delta,0),'test')
                actual_duration=sequence.get_duration()
                record={'probe':name,'sdk_status':'accepted','requested_duration_ns':duration,'actual_duration_ns':actual_duration,'qpu_backend_constraints_checked':False,'device_requires_layout':device.requires_layout}
            except Exception as error:
                record={'probe':name,'sdk_status':'rejected','exception':type(error).__name__,'message':str(error),'qpu_backend_constraints_checked':False}
            record['warnings']=[str(w.message) for w in caught]
            records.append(record)
    return records


def execute(output):
    start=time.perf_counter();cpu=time.process_time();output.mkdir(parents=True,exist_ok=True)
    require(not (output/'raw.jsonl').exists(),'raw output already exists')
    pulser,QutipEmulator=sdk_imports();device=pulser.AnalogDevice
    c6=float(device.interaction_coeff);channel=device.channels['rydberg_global']
    count=0;max_prob=0;max_h=0;max_norm=0
    with (output/'raw.jsonl').open('x') as raw:
        for distance,omega,delta,phase,duration in itertools.product((6,10,14),(0,1,2),(-1,0,1),(0,math.pi/2),(100,500,1000)):
            interaction=c6/distance**6
            expected_h=hamiltonian(omega,delta,phase,interaction)
            require(max(abs(expected_h[i][j]-expected_h[j][i].conjugate()) for i in range(4) for j in range(4))<1e-12,'oracle not Hermitian')
            expected=oracle_probabilities(expected_h,duration/1000)
            sequence=build(pulser,distance,duration,omega,delta,phase)
            require(sequence.get_duration()==duration,'pulse changed by SDK')
            emulator=QutipEmulator.from_sequence(sequence,sampling_rate=1.0,evaluation_times='Minimal',with_modulation=False)
            observed_h=emulator.get_hamiltonian(0).full()
            h_error=max(abs(complex(observed_h[3-i,3-j])-expected_h[i][j]) for i in range(4) for j in range(4))
            result=emulator.run(atol=1e-10,rtol=1e-10,max_step=0.001)
            amplitudes=result.get_final_state(ignore_global_phase=False,normalize=False).full().ravel()
            observed=[float(abs(amplitudes[3-i])**2) for i in range(4)]
            prob_error=max(abs(p-q) for p,q in zip(expected,observed))
            norm_error=max(abs(sum(expected)-1),abs(sum(observed)-1))
            passed=h_error<HAMILTONIAN_TOLERANCE and prob_error<PROBABILITY_TOLERANCE and norm_error<NORMALIZATION_TOLERANCE
            record={'evaluation':count,'distance_um':distance,'omega_rad_per_us':omega,'delta_rad_per_us':delta,'phase_rad':phase,'duration_ns':duration,'interaction_rad_per_us':interaction,'oracle_probabilities_gg_gr_rg_rr':expected,'sdk_probabilities_gg_gr_rg_rr':observed,'hamiltonian_error':h_error,'probability_error':prob_error,'normalization_error':norm_error,'sdk_accepted':True,'device':'AnalogDevice','device_constructor_constraints_checked':True,'qpu_backend_constraints_checked':False,'specific_hardware_compatible':'unverified','qpu_executed':False,'status':'passed' if passed else 'failed'}
            raw.write(json.dumps(record,allow_nan=False)+'\n');raw.flush()
            require(passed,'finite Hamiltonian/ODE comparison failed')
            count+=1;max_prob=max(max_prob,prob_error);max_h=max(max_h,h_error);max_norm=max(max_norm,norm_error)
    require(count==162,'grid incomplete')
    device_record={name:getattr(device,name) for name in ('name','dimensions','rydberg_level','min_atom_distance','max_atom_num','max_radial_distance','max_sequence_duration','requires_layout','max_layout_filling','accepts_new_layouts')}
    device_record['interaction_coeff']=c6
    device_record['rydberg_global']={name:getattr(channel,name) for name in ('addressing','max_amp','max_abs_detuning','min_duration','clock_period','max_duration')}
    metrics={'evaluations':count,'max_probability_error':max_prob,'max_hamiltonian_error':max_h,'max_normalization_error':max_norm,'tolerances':{'probability':PROBABILITY_TOLERANCE,'hamiltonian':HAMILTONIAN_TOLERANCE,'normalization':NORMALIZATION_TOLERANCE},'software':{'python':platform.python_version(),**{name:importlib.metadata.version(name) for name in ('pulser','pulser-core','pulser-simulation','qutip','numpy','scipy')}},'device':device_record,'sdk_probes':probes(pulser),'sampling_rate':1.0,'with_modulation':False,'noise':False,'solver_options':{'atol':1e-10,'rtol':1e-10,'max_step_us':0.001},'oracle':'separate4x4Hamiltonian construction with numpy Hermitian eigendecomposition, initial|gg>','sdk_solver':'QutipEmulator, no-noise ODE','python_optimization':sys.flags.optimize,'elapsed_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,'external_purchase_eur':0,'qpu_jobs':0,'specific_hardware_compatible':'unverified','independent_review':'pending'}
    (output/'metrics.json').write_text(json.dumps(metrics,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:metrics[k] for k in ('evaluations','max_probability_error','max_hamiltonian_error','max_normalization_error','elapsed_seconds','qpu_jobs')}))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);args=parser.parse_args();execute(args.output)


if __name__=='__main__':main()
