import ldap
import logging
logger = logging.getLogger('bda.pasldap')


WHAT_TO_DEBUG = set([
    'authentication',
    'properties',
    'userenumeration',
    ])


def wrapfunc(old, new):
    new.func_name = old.func_name
    new.__doc__ = old.__doc__
    new.wrapped = old
    return new


def debug(aspects=None):
    """generate decorator which helps to control what aspects of a program to debug
    on per-function basis. Aspects are provided as list of arguments.
    It DOESN'T slowdown functions which aren't supposed to be debugged.
    """
    aspects = set(aspects)
    def decorator(func):
        if aspects & WHAT_TO_DEBUG:
            def newfunc(*args, **kws):
                logger.debug('%s: args=%s, kws=%s', func.func_name, args, kws)
                result = func(*args, **kws)
                logger.debug('%s: --> %s', func.func_name, result)
                return result
            return wrapfunc(func, newfunc)
        else:
            return func
    return decorator


def ifnotenabledreturn(default=None, enabled_attr="enabled"):
    """generate decorator that checks whether plugin is enabled, returns retval
    otherwise
    """
    def decorator(method):
        def wrapper(self, *args, **kws):
            if not getattr(self, enabled_attr):
                logger.info('disabled; %s defaulting.' % \
                        (method.func_name,))
                return default
            return method(self, *args, **kws)
        return wrapfunc(method, wrapper)
    return decorator

def if_groups_not_enabled_return(default=None):
    return ifnotenabledreturn(default, "groups_enabled")

def if_users_not_enabled_return(default=None):
    return ifnotenabledreturn(default, "users_enabled")
