from django.db.models import Sum
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import ModelSerializer
from warehouses.serializers import WarehouseSerializer
from others.rv_ball import rv_ball
from users.models import *
from users.serializers import UsersTreeSerializer, ForOthersUsersSerializer
from warehouses.models import WarehouseSaleProduct, Warehouse


DISTRIBUTER, KONSULTANT, MENEJER, MENEJER_PRO, SUPERVISOR, GOLD, PLATINUM, DIAMOND = ("Distributer", "Konsultant", "Menejer", "Menejer Pro", "Supervisor", "Gold", "Platinum", "Diamond")

EXTRA_BONUSES_PARAMETRS ={
    DISTRIBUTER: 0,
    KONSULTANT: 50000,
    MENEJER: 200000,
    MENEJER_PRO: 700000,
    SUPERVISOR: 1500000,
    GOLD: 4000000,
    PLATINUM: 7000000,
    DIAMOND: 10000000
}

# def get_user_tree(user_id: str, month: str):
#     month = str(month)[:7]
#     tree = []
#     id = [str(user_id)]
#
#     sanoq = 1
#     while len(id) > 0:
#         sanoq += 1
#         user_tree1 = UsersTree.objects.filter(offerer__id=id[0]).filter(deleted=False)
#
#         for follower in user_tree1:
#             user = UsersTreeSerializer(follower)
#             tree.append(user.data['invited'])
#             id.append(str(user.data['invited']['id']))
#
#         id.pop(0)
#     return {
#         "tree": tree
#     }


def get_user_tree_sales_summa(user_id: int, month: str):
    month = str(month)[:7]
    tree_score = 0
    tree = []
    tree_statuses = []
    id = [str(user_id)]
    extra_bonus = 0
    sanoq = 1

    user_sales = WarehouseSaleProduct.objects.filter(user__user_id=user_id, dateTime__startswith=month).aggregate(Sum('summa'))
    user_score = user_sales['summa__sum'] / rv_ball["BALL"] if user_sales['summa__sum'] is not None else 0
    tree_score += user_score

    while len(id) > 0:
        sanoq += 1
        user_tree1 = UsersTree.objects.filter(offerer__user_id=id[0]).filter(deleted=False)

        for follower in user_tree1:
            salary = UserSalary.objects.filter(month__startswith=month, user=follower.invited)
            if len(salary) > 0:
                extra_bonus += EXTRA_BONUSES_PARAMETRS[salary[0].user_status]
                tree_score += float(salary[0].user_score)
                tree.append(
                    {
                        "follower_user_id": int(follower.invited.user_id),
                        "follower_uuid": str(follower.invited.id),
                        "follower_tree_score": int(salary[0].user_tree_score),
                        "follower_status": str(salary[0].user_status),
                        "follower_stat_percent": int(salary[0].stat_percent),
                    }
                )
                follower_status = str(salary[0].user_status)
                if follower_status != DISTRIBUTER and follower_status not in tree_statuses:
                    tree_statuses.append(follower_status)
            id.append(str(follower.invited.user_id))

        id.pop(0)
    return {
        "tree_score": tree_score,
        "extra_bonus": extra_bonus,
        "tree": tree,
        "user_score": user_score,
        "tree_statuses": tree_statuses,
    }


def get_for_mentorship_first_tree_bonus_15_percent(user_id: int, month: str):
    month = str(month)[:7]
    user_first_tree = UsersTree.objects.filter(offerer__user_id=user_id).filter(deleted=False)
    forMentorship = 0

    for follower in user_first_tree:
        sales = WarehouseSaleProduct.objects.filter(user=follower.invited, dateTime__startswith=month).aggregate(Sum('summa'))
        if sales['summa__sum'] is not None:
            forMentorship += sales['summa__sum'] / rv_ball["BALL"] * 0.15 * rv_ball["RV"]

    return forMentorship


def get_personal_bonus(user_id: int, month: str):
    month = str(month)[:7]
    sales = WarehouseSaleProduct.objects.filter(user__user_id=user_id, dateTime__startswith=month).aggregate(Sum('summa'))
    user_score = sales['summa__sum'] / rv_ball["BALL"] if sales['summa__sum'] is not None else 0
    personal_bonus = user_score * 0.4 * rv_ball["RV"]

    return {
        "user_score": user_score,
        "personal_bonus": personal_bonus,
        "forMentorship": get_for_mentorship_first_tree_bonus_15_percent(user_id=user_id, month=month)
    }


def get_status(user_id: int, month: str):
    personal_bonus = get_personal_bonus(user_id=user_id, month=month)
    tree_sales_summa = get_user_tree_sales_summa(user_id=user_id, month=month)
    user_tree_score = tree_sales_summa['tree_score']

    if user_tree_score >= 100000:
        status = DIAMOND
        status_percent = 33
    elif user_tree_score >= 70000:
        status = PLATINUM
        status_percent = 30
    elif user_tree_score >= 40000:
        status = GOLD
        status_percent = 27
    elif user_tree_score >= 15000:
        status = SUPERVISOR
        status_percent = 23
    elif user_tree_score >= 7000:
        status = MENEJER_PRO
        status_percent = 19
    elif user_tree_score >= 2000:
        status = MENEJER
        status_percent = 15
    elif user_tree_score >= 500:
        status = KONSULTANT
        status_percent = 10
    else:
        status = DISTRIBUTER
        status_percent = 0

    personal_bonus.update(tree_sales_summa)
    personal_bonus['user_status'] = status
    personal_bonus['status_percent'] = status_percent

    return personal_bonus


def get_status_by_tree_score(user_tree_score: float):
    if user_tree_score >= 100000:
        status = DIAMOND
        status_percent = 33
    elif user_tree_score >= 70000:
        status = PLATINUM
        status_percent = 30
    elif user_tree_score >= 40000:
        status = GOLD
        status_percent = 27
    elif user_tree_score >= 15000:
        status = SUPERVISOR
        status_percent = 23
    elif user_tree_score >= 7000:
        status = MENEJER_PRO
        status_percent = 19
    elif user_tree_score >= 2000:
        status = MENEJER
        status_percent = 15
    elif user_tree_score >= 500:
        status = KONSULTANT
        status_percent = 10
    else:
        status = DISTRIBUTER
        status_percent = 0

    return {
        "user_status": status,
        "status_percent": status_percent
    }


def check_user_status(user_id: int, month: str):
    data = get_status(user_id=user_id, month=month)
    for_minus_scores = 0
    status = {"user_status": data['user_status'], "status_percent": data['status_percent']}

    if DISTRIBUTER in data['tree_statuses']:
        data['tree_statuses'].remove(DISTRIBUTER)
    while status['user_status'] in data['tree_statuses']:
        for follower_data in data['tree']:
            if status == follower_data['follower_status']:
                for_minus_scores += follower_data['follower_tree_score']
        status = get_status_by_tree_score(user_tree_score=float(data['tree_score'] - for_minus_scores))
        for_minus_scores = 0

    for_followers_status_percent = 0
    if status['status_percent'] != 0:
        for_followers_status_percent += data['user_score'] * (status['status_percent'] / 100) * rv_ball['RV']

    blocked_followers = []
    for follower in data['tree']:
        user_tree = UsersTree.objects.filter(invited__user_id=follower['follower_user_id'])
        followers_teachers_user_id = user_tree[0].offerer.user_id
        if user_tree[0].offerer.id == user_id:
            take_bonus = True
        elif followers_teachers_user_id not in blocked_followers:
            take_bonus = True
        else:
            take_bonus = False

        difference_of_status_percent = status['status_percent'] - follower['follower_stat_percent']
        if take_bonus and difference_of_status_percent > 0:
            for_followers_status_percent += follower['follower_tree_score'] * (difference_of_status_percent / 100) * rv_ball['RV']
            blocked_followers.append(follower['follower_user_id'])

    data.update(
        {
            "user_status": status['user_status'],
            "status_percent": status['status_percent'],
            "for_minus_scores": for_minus_scores,
            "for_followers_status_percent": for_followers_status_percent,
        }
    )
    return data


def get_salary_data(user_id: int | str, month: str):
    if User.objects.filter(id=user_id).exists():
        user = User.objects.filter(id=user_id)
        user_ID = user[0].user_id
        first_name = user[0].first_name
        last_name = user[0].last_name
        phone_number = user[0].phone_number
        salary = check_user_status(user_id=user[0].user_id, month=month)
    else:
        user = User.objects.filter(user_id=user_id)
        salary = check_user_status(user_id=user_id, month=month)
        user_ID = user_id
        first_name = user[0].first_name
        last_name = user[0].last_name
        phone_number = user[0].phone_number

    warehouse = Warehouse.objects.get(id="57e06190-7c22-44a0-9b47-2ce314ddd809")
    warehouse = WarehouseSerializer(warehouse).data
    salary['first_name'] = first_name
    salary['last_name'] = last_name
    salary['phone_number'] = phone_number
    salary['user_id'] = user_ID
    salary['warehouse'] = warehouse
    salary['coupon'] = 0
    salary['paid'] = 0
    salary['debt'] = 0
    salary['bonus_for_followers_status'] = 0
    salary['collective_bonus_amount'] = 0
    salary['stat_percent'] = salary['status_percent']
    salary['user_tree_score'] = salary['tree_score']
    salary['user_tree_summa'] = salary['tree_score'] * rv_ball['BALL']
    if salary['user_score'] >= 50:
        salary['salary'] = salary['personal_bonus'] + salary['forMentorship'] + salary['extra_bonus'] + salary['for_followers_status_percent']
        return salary
    else:
        salary.pop("tree")
        salary['extra_bonus'] = 0
        salary['forMentorship'] = 0
        salary['status_percent_bonus'] = 0
        salary['salary'] = salary['personal_bonus'] + salary['forMentorship'] + salary['extra_bonus'] + salary['for_followers_status_percent']
        return salary
