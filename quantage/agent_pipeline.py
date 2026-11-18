"""Execute recorded agent proposals through explicit local-only boundaries.

The original text is preserved. A finite numerical certificate does not certify
its interpretation. Gold annotations are never imported by this module.
"""
from .contracts import ContractError, keys, need, normalize_problem, validate_model, verify_external
from .core import MIS_INTENT, PHOTO_INTENT, understand, solve_qubo, optical_probabilities


def process_proposal(request, proposal, numerical=True):
    try:
        keys(proposal, ('id','action','problem','formulation','solver','reason'))
        need(type(proposal['id']) is str and type(proposal['reason']) is str, 'id and reason must be strings')
        need(proposal['action'] in ('propose','abstain'), 'unknown action')
        if proposal['action'] == 'abstain':
            need(all(proposal[k] is None for k in ('problem','formulation','solver')), 'abstention must not carry executable fields')
            return {'status':'abstain','stage':'agent_decision','reason':proposal['reason']}
        p=normalize_problem(proposal['problem'])
        intent=MIS_INTENT if p['family']=='mis' else PHOTO_INTENT
        original=understand({'intent':intent,'data':request['data']})
        need(p == original, 'proposed problem changes numerical input or supported contract fields')
        model=proposal['formulation'];validate_model(p,model)
        route=proposal['solver']
        keys(route, ('local_solver','quantum_provider','hardware_status','execution_kind'))
        expected='exhaustive_qubo' if p['family']=='mis' else 'single_photon_amplitudes'
        provider='Pasqal' if p['family']=='mis' else 'Quandela'
        need(route['local_solver']==expected and route['execution_kind']=='local', 'unsupported local solver or execution type')
        need(route['quantum_provider'] in (provider,None), 'unsupported project provider for this formulation')
        need(route['hardware_status']=='unverified', 'physical compatibility or account access is not established')
        report=verify_external(p,model) if numerical else {'valid':None,'stage':'not_applied'}
        if numerical and not report['valid']:
            return {'status':'abstain','stage':'numerical_verifier','verification':report}
        solution=solve_qubo(model) if p['family']=='mis' else {'probabilities':optical_probabilities(model)}
        return {'status':'accepted','stage':'verified_output' if numerical else 'schema_only',
                'problem':p,'formulation':model,'solution':solution,'route':route,'verification':report,
                'execution':'local_only','hardware_readiness':'unverified','qpu_submitted':False,
                'semantic_certificate':False,'original_intent':request['intent']}
    except (ContractError,KeyError,TypeError,ValueError,IndexError,OverflowError) as exc:
        return {'status':'abstain','stage':'contract_boundary','reason':str(exc)}
