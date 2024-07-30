from spirl.configs.hrl.maze.easy.spirl.conf import *
from spirl.models.closed_loop_vq_spirl_mdl import ClVQSPiRLMdl
from spirl.rl.policies.cl_model_policies import ClModelPolicy
from spirl.rl.policies.tree_policies import CARTPolicy
from spirl.rl.agents.tree_agent import CARTAgent

# update model params to conditioned decoder on state
ll_model_params.cond_decode = True

ll_model_params.update(AttrDict(
    codebook_K=16,
))

prior_model_epoch = 73

# create LL closed-loop policy
ll_policy_params = AttrDict(
    policy_model=ClVQSPiRLMdl,
    policy_model_params=ll_model_params,
    policy_model_checkpoint=os.path.join(os.environ["EXP_DIR"],
                                         "skill_prior_learning/maze/easy/hierarchical_cl_vq"),
    policy_model_epoch=prior_model_epoch,
)
ll_policy_params.update(ll_model_params)
0
# create LL SAC agent (by default we will only use it for rolling out decoded skills, not finetuning skill decoder)
ll_agent_config = AttrDict(
    policy=ClModelPolicy,
    policy_params=ll_policy_params,
    critic=MLPCritic,  # LL critic is not used since we are not finetuning LL
    critic_params=hl_critic_params
)

# oracle_policy_params = hl_policy_params
#
# oracle_policy_params.update(AttrDict(
#     policy=LearnedVQPriorAugmentedPolicy,
#     prior_model=ll_policy_params.policy_model,
#     prior_model_params=ll_policy_params.policy_model_params,
#     prior_model_checkpoint=ll_policy_params.policy_model_checkpoint,
#     policy_model_checkpoint=os.path.join(os.environ["EXP_DIR"],
#                                          "hrl/kitchen/spirl_cl_vq/mlsh_k16_s0"),
# ))

hl_agent_config.policy = CARTPolicy

# update HL policy model params
hl_policy_params.update(AttrDict(
    policy=CARTPolicy,
    policy_model_checkpoint=os.path.join(os.environ["EXP_DIR"],
                                         "/home/wenyongyan/文档/DAGGER+CART/maze/easy/cart_1000_d9.pkl"),
    codebook_checkpoint=os.path.join(os.environ["EXP_DIR"],
                                     "hrl/maze/easy/spirl_cl_vq/k16_s0_r/weights/weights_ep24.pth"),
    # max_depth=10,
    # oracle_policy=LearnedVQPriorAugmentedPolicy,
    prior_model=ll_policy_params.policy_model,
    prior_model_params=ll_policy_params.policy_model_params,
    prior_model_checkpoint=ll_policy_params.policy_model_checkpoint,
))

# register new LL agent in agent_config and turn off LL agent updates
agent_config.update(AttrDict(
    hl_agent=CARTAgent,
    hl_agent_params=hl_agent_config,
    ll_agent=SACAgent,
    ll_agent_params=ll_agent_config,
    update_ll=False,
))