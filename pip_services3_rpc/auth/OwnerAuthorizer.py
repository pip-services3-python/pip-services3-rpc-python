# -*- coding: utf-8 -*-

from pip_services3_commons.errors.UnauthorizedException import UnauthorizedException
from pip_services3_rpc.services.HttpResponseSender import HttpResponseSender


class OwnerAuthorizer:

    def owner(self, id_param='user_id'):
        def inner(req=None, res=None, next=None, ):
            if req.user is None:
                HttpResponseSender.send_error(UnauthorizedException(
                    None,
                    'NOT_SIGNED',
                    'User must be signed in to perform this operation'
                ).with_status(401))
            else:
                user_id = req.route.params[id_param]
                if req.user_id != user_id:
                    HttpResponseSender.send_error(UnauthorizedException(
                        None,
                        'FORBIDDEN',
                        'Only data owner can perform this operation'
                    ).with_status(403))
                else:
                    next()

        return inner

    def owner_or_admin(self, id_param='user_id', ):
        def inner(req, res, next):
            if req.user is None:
                HttpResponseSender.send_error(UnauthorizedException(
                    None,
                    'NOT_SIGNED',
                    'User must be signed in to perform this operation'
                ).with_status(401))
            else:
                user_id = req.route.params[id_param] or req.param(id_param)
                if req.user is not None:
                    roles = req.user.roles
                else:
                    roles = None
                admin = 'admin' in roles
                if req.user_id != user_id and not admin:
                    HttpResponseSender.send_error(UnauthorizedException(
                        None,
                        'FORBIDDEN',
                        'Only data owner can perform this operation'
                    ).with_status(403))
                else:
                    next()

        return inner
