import stable_baselines3.dqn

from spirl.configs.hrl.calvin.spirl.conf import *
from spirl.models.closed_loop_vq_spirl_mdl import ClVQSPiRLMdl
from spirl.rl.policies.cl_model_policies import ClModelPolicy
from spirl.rl.policies.dqn_policies import DQNPolicy
from spirl.rl.agents.dqn_agent import DQNAgent
from spirl.rl.policies.prior_dqn_polices import PriorWarmupDQNPolicy

# update model params to conditioned decoder on state
ll_model_params.cond_decode = True

ll_model_params.update(AttrDict(
    codebook_K=8,
    # fixed_codebook=False,
))

# create LL closed-loop policy
ll_policy_params = AttrDict(
    policy_model=ClVQSPiRLMdl,
    policy_model_params=ll_model_params,
    policy_model_checkpoint=os.path.join(os.environ["EXP_DIR"],
                                         "skill_prior_learning/calvin/hierarchical_cl_vq/K_8"),
)
ll_policy_params.update(ll_model_params)

# create LL SAC agent (by default we will only use it for rolling out decoded skills, not finetuning skill decoder)
ll_agent_config = AttrDict(
    policy=ClModelPolicy,
    policy_params=ll_policy_params,
    critic=MLPCritic,  # LL critic is not used since we are not finetuning LL
    critic_params=hl_critic_params
)

hl_agent_config.policy = PriorWarmupDQNPolicy

# update HL policy model params
hl_policy_params.update(AttrDict(
    policy=hl_agent_config.policy,
    prior_model=ll_policy_params.policy_model,
    prior_model_params=ll_policy_params.policy_model_params,
    prior_model_checkpoint=ll_policy_params.policy_model_checkpoint,
    codebook_checkpoint=os.path.join(os.environ["EXP_DIR"],
                                     "skill_prior_learning/calvin/hierarchical_cl_vq/K_8/weights/weights_ep99.pth"),
    codebook_K=ll_model_params.codebook_K,
    policy_lr=1e-4,
    target_update_interval=10000,
    epsilon=0,
    eps_end=0,
    eps_decay=0,
    max_size=500000,
    batch_size=256,
    hidden_layers=[128, 128, 128],
))

# register new LL agent in agent_config and turn off LL agent updates
agent_config.update(AttrDict(
    hl_agent=DQNAgent,
    hl_agent_params=hl_agent_config,
    ll_agent=SACAgent,
    ll_agent_params=ll_agent_config,
    update_ll=False,
))
