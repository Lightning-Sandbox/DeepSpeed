import deepspeed

from tests.unit.common import DistributedTest
from tests.unit.simple_model import *

from tests.unit.checkpoint.common import checkpoint_correctness_verification


class TestLatestCheckpoint(DistributedTest):
    world_size = 1

    def test_existing_latest(self, tmpdir):
        config_dict = {
            "train_batch_size": 2,
            "steps_per_print": 1,
            "optimizer": {
                "type": "Adam",
                "params": {
                    "lr": 0.00015
                }
            }
        }
        hidden_dim = 10
        args = args_from_dict(tmpdir, config_dict)
        models = [SimpleModel(hidden_dim=hidden_dim) for _ in range(2)]

        def _helper(args, models):
            checkpoint_correctness_verification(args,
                                                models=models,
                                                hidden_dim=hidden_dim,
                                                tmpdir=tmpdir,
                                                load_optimizer_states=True,
                                                load_lr_scheduler_states=False,
                                                fp16=False,
                                                empty_tag=True)

        _helper(args, models)

    def test_missing_latest(self, tmpdir):
        config_dict = {
            "train_batch_size": 2,
            "steps_per_print": 1,
            "optimizer": {
                "type": "Adam",
                "params": {
                    "lr": 0.00015
                }
            }
        }
        hidden_dim = 10
        args = args_from_dict(tmpdir, config_dict)

        model = SimpleModel(hidden_dim)

        def _helper(args, model):
            model, _, _,_ = deepspeed.initialize(args=args,
                                                model=model,
                                                model_parameters=model.parameters())
            # should be no-op, since latest doesn't exist
            model.load_checkpoint(tmpdir)

        _helper(args=args, model=model)
