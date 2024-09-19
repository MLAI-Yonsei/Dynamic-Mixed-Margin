import torch
import random
from torch import nn

from .BaseLoss import BaseLoss


class SumTripletLossDML(BaseLoss):
    """Class of Triplet Loss taking sum of negative sample."""

    def __init__(self, margin: float = 1, regularizers: list = []):
        super().__init__(regularizers)
        self.margin = margin
        self.ReLU = nn.ReLU()

    def main(
        self, embeddings_dict: dict, batch: torch.Tensor, column_names: dict
    ) -> torch.Tensor:
        """Method of forwarding main loss

        Args:
            embeddings_dict (dict): A dictionary of embddings which has following key and values
                user_embedding : embeddings of user, size (n_batch, 1, d)
                pos_item_embedding : embeddings of positive item, size (n_batch, 1, d)
                neg_item_embedding : embeddings of negative item, size (n_batch, n_neg_samples, d)

            batch (torch.Tensor) : A tensor of batch, size (n_batch, *).
            column_names (dict) : A dictionary that maps names to indices of rows of batch.

        Return:
            torch.Tensor : loss, L = Σ [m + pos_dist^2 - min(neg_dist)^2]
        """
        pos_dist = torch.cdist(
            embeddings_dict["user_embedding"], embeddings_dict["pos_item_embedding"]
        )
        lamb = random.random()
        # while lamb < 0.5:
        #     lamb = random.random()
        n_neg_samples = embeddings_dict["neg_item_embedding"].shape[1]
        pos_embeddings = torch.repeat_interleave(embeddings_dict["pos_item_embedding"],
                                                 repeats=n_neg_samples,
                                                 dim=1)
        neg_embeddings = lamb * pos_embeddings + (1-lamb) * embeddings_dict["neg_item_embedding"]
        neg_dist = torch.cdist(
            embeddings_dict["user_embedding"], neg_embeddings
        )

        self.margin = self.margin * lamb
        tripletloss = self.ReLU(self.margin + pos_dist ** 2 - neg_dist ** 2)
        loss = torch.mean(tripletloss)

        return loss
