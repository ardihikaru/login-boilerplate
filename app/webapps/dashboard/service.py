from typing import Dict, List
from app.db.adapters.user.user import get_users, get_session_today, get_sessions_last_7days, get_unverified_users
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from math import ceil


async def load_user_data(session: AsyncSession, order_desc: bool = False) -> List:
    """ Load user data with an optional parameter to order the results

    :param session:
    :param order_desc:
    :return:
    """
    return await get_users(session, order_desc=order_desc)


async def load_unverified_users_by_month(session: AsyncSession) -> List:
    """ Load unverified list of users filtered by month

    :param session:
    :return:
    """
    # get this month
    this_month = datetime.utcnow().month

    return await get_unverified_users(session, month=this_month)


async def get_7days_total_avg_session(session: AsyncSession) -> int:
    """ Extract 7 days backwards and count total number of active users each day, then get the average value

    :param session:
    :return:
    """
    # get the data
    session_7days = await get_sessions_last_7days(session)

    # convert into a list
    data_list = []
    for data in session_7days:
        data_list.append(data["total"])

    # calc average value and return
    avg_session_users = sum(data_list) / len(data_list)
    return int(ceil(avg_session_users))


async def get_statistics(session: AsyncSession, total_users: int) -> Dict:
    """ Load the summary of the statistic user data

    :param session:
    :param total_users:
    :return:
    """
    statistics = {
        "total_users": total_users,
        "total_session_today": len(await get_session_today(session)),
        "total_session_7days": await get_7days_total_avg_session(session),
        "total_unver_acc_tmonth": len(await load_unverified_users_by_month(session)),
    }

    return statistics


async def dummy_traffic_data() -> Dict:
    """ Generate dummy traffic data (TBD)

    :return:
    """
    pass


async def dummy_registration_data() -> Dict:
    """ Generate dummy registration data (TBD)

    :return:
    """
    pass
