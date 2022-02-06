from sqlalchemy.exc import IntegrityError


async def get_pgsql_integrity_error_msg(err: IntegrityError):
    raw_message = err.orig.args[0].splitlines()

    err_msg = raw_message[-1].replace("DETAIL:", "").lstrip()

    return err_msg
