class DuplicateSignMixin:

    def reportDuplicateSign(self, typ, data, from_address, transaction_cfg=None):
        """
        Report duplicate sign
        :param typ: Represents duplicate sign type, 1:prepareBlock, 2: prepareVote, 3:viewChange
        :param data: Json value of single evidence, format reference RPC interface Evidences
        :param from_address: address for transaction
        :param transaction_cfg:
        :return:
        """
        pri_key = self._account.find_pri_key(from_address)
        return self._ppos.reportDuplicateSign(typ, data, pri_key, transaction_cfg)
