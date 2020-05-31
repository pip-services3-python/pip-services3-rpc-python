# -*- coding: utf-8 -*-

from pip_services3_commons.errors.UnauthorizedException import UnauthorizedException
from pip_services3_rpc.services.HttpResponseSender import HttpResponseSender


class BasicAuthorizer:

    def anybody(self):
        return lambda req, res, next: next()

    def signed(self):
        def inner(req, res, next):
            if req.user is None:
                HttpResponseSender.send_error(UnauthorizedException(
                    None,
                    'NOT_SIGNED',
                    'User must be signed in to perform this operation '
                ).with_status(401))
            else:
                next()

        return inner
