import torch.optim as optim
from collections import Counter
import warnings

class WarmupScheduler(optim.lr_scheduler._LRScheduler):
    def __init__(self, optimizer, warmup_epochs, initial_lr, max_lr, milestones, gamma=0.1, last_epoch=-1):
        assert warmup_epochs < milestones[0]
        self.warmup_epochs = warmup_epochs
        self.milestones = Counter(milestones)
        self.gamma = gamma

        initial_lrs = self._format_param("initial_lr", optimizer, initial_lr)
        max_lrs = self._format_param("max_lr", optimizer, max_lr)
        if last_epoch == -1:
            for idx, group in enumerate(optimizer.param_groups):
                group["initial_lr"] = initial_lrs[idx]
                group["max_lr"] = max_lrs[idx]

        super(WarmupScheduler, self).__init__(optimizer, last_epoch)

    def get_lr(self):
        if not self._get_lr_called_within_step:
            warnings.warn("To get the last learning rate computed by the scheduler, "
                          "please use `get_last_lr()`.", DeprecationWarning)

        if self.last_epoch <= self.warmup_epochs:
            pct = self.last_epoch / self.warmup_epochs
            return [
                (group["max_lr"] - group["initial_lr"]) * pct + group["initial_lr"]
                for group in self.optimizer.param_groups]
        else:
            if self.last_epoch not in self.milestones:
                return [group['lr'] for group in self.optimizer.param_groups]
            return [group['lr'] * self.gamma ** self.milestones[self.last_epoch]
                    for group in self.optimizer.param_groups]

    @staticmethod
    def _format_param(name, optimizer, param):
        """Return correctly formatted lr/momentum for each param group."""
        if isinstance(param, (list, tuple)):
            if len(param) != len(optimizer.param_groups):
                raise ValueError("expected {} values for {}, got {}".format(
                    len(optimizer.param_groups), name, len(param)))
            return param
        else:
            return [param] * len(optimizer.param_groups)

