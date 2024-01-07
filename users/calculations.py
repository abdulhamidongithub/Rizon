from django.db.models import Sum
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import ModelSerializer
from users.marketing_plan_2_0 import user_all_bonuses_mp_2_0, get_all_shajara_mp_2_0
from users.new_mp_test import get_salary_data
from warehouses.serializers import WarehouseSerializer
from others.rv_ball import rv_ball
from users.models import *
from users.serializers import UsersTreeSerializer, ForOthersUsersSerializer
from warehouses.models import WarehouseSaleProduct, Warehouse


DISTRIBUTER, KONSULTANT, MENEJER, MENEJER_PRO, SUPERVISOR, GOLD, PLATINUM, DIAMOND = ("None", "Konsultant", "Menejer", "Menejer Pro", "Supervisor", "Gold", "Platinum", "Diamond")
CASHBACK_AMOUNT, VOUCHER_AMOUNT, TRAVEL_AMOUNT, UMRAH_AMOUNT, AUTOBONUS_AMOUNT_1, AUTOBONUS_AMOUNT_2, AUTOBONUS_AMOUNT_3 = (165000, 750000, 1000000, 6000000, 16000000, 28000000, 40000000)


BONUSES = {
    KONSULTANT: {CASHBACK: CASHBACK_AMOUNT},
    MENEJER: {VOUCHER: VOUCHER_AMOUNT},
    MENEJER_PRO: {VOUCHER: VOUCHER_AMOUNT, TRAVEL: TRAVEL_AMOUNT},
    SUPERVISOR: {VOUCHER: VOUCHER_AMOUNT, TRAVEL: TRAVEL_AMOUNT, UMRAH: UMRAH_AMOUNT},
    GOLD: {VOUCHER: VOUCHER_AMOUNT, TRAVEL: TRAVEL_AMOUNT, AUTOBONUS: AUTOBONUS_AMOUNT_1},
    PLATINUM: {VOUCHER: VOUCHER_AMOUNT, TRAVEL: TRAVEL_AMOUNT, AUTOBONUS: AUTOBONUS_AMOUNT_2},
    DIAMOND: {VOUCHER: VOUCHER_AMOUNT, TRAVEL: TRAVEL_AMOUNT, AUTOBONUS: AUTOBONUS_AMOUNT_3}
    }


def create_user_bonus_account(data: dict):
    try:
        for bonus_type, bonus_amount in BONUSES[data['status']].items():
            BonusAccount.objects.create(
                bonus_type=bonus_type,
                user=User.objects.get(id=data['id']),
                status=data['status'],
                amount=bonus_amount,
                month=data['month'],
                # comment=f"{data['month']} oyidagi {data['status']} statusi uchun {bonus_type} bonus"
                comment=f"{data['status']} statusi uchun {bonus_type} bonus"
            )
    except Exception as e:
        print(f"{e=}")


def calculate_user_bonus_account(data: dict):
    BonusAccount.objects.filter(month=data['month'], user__id=data['id']).delete()
    # status = data['status']
    create_user_bonus_account(data=data)

class UserSalarySerializer(ModelSerializer):
    # user = ForOthersUsersSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)

    class Meta:
        model = UserSalary
        fields = "__all__"


class UserSalarySerializerTest(ModelSerializer):
    user = ForOthersUsersSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)

    class Meta:
        model = UserSalary
        fields = "__all__"


def insteadUserSalarySerializer(users, many=True):
    if many==False:
        user_ser = UserSalarySerializerTest(users).data
        data = user_ser.pop('user')
        user_ser.pop("id")
        data.update(user_ser)

        return data
    else:
        all_data = []
        for user in users:
            user_ser = UserSalarySerializerTest(user).data
            data = user_ser.pop('user')
            user_ser.pop("id")
            data.update(user_ser)

            all_data.append(data)

        return all_data


def shajara_malumotlari_2_0(user_id: str):
    users_Data = {}
    avlod_sanoq = 1
    id = [user_id]
    id_2 = []

    while len(id) > 0:
        data_sheets = UsersTree.objects.filter(offerer__id=id[0]).filter(deleted=False)

        for qator in data_sheets:
            user_ser = UsersTreeSerializer(qator)
            if user_ser.data['offerer']['id'] == id[0]:
                if str(avlod_sanoq) in users_Data:
                    users_Data[f"{avlod_sanoq}"].append(user_ser.data['invited'])
                else:
                    users_Data[f"{avlod_sanoq}"] = []
                    users_Data[f"{avlod_sanoq}"].append(user_ser.data['invited'])

                id_2.append(user_ser.data['invited']['id'])

        id.pop(0)
        if len(id) == 0:
            avlod_sanoq += 1
            id = id_2
            id_2 = []

    return users_Data


def get_user_tree(user_id: str):
    tree = []
    id = [str(user_id)]

    sanoq = 1
    while len(id) > 0:
        # print(sanoq)
        sanoq += 1

        user_tree1 = UsersTree.objects.filter(offerer__id=id[0]).filter(deleted=False)

        for follower in user_tree1:
            user = UsersTreeSerializer(follower)
            tree.append(user.data['invited'])
            id.append(str(user.data['invited']['id']))

        id.pop(0)
    return {"tree": tree}


def mentorship_bonus_for_actives(user_id: str, date: str):
    user_tree = UsersTree.objects.filter(offerer__id=user_id).filter(deleted=False)
    actives = 0
    forMentorship = 0
    # print(f"====================mentorship_bonus_for_actives==============================")
    # print(f"====================mentorship_bonus_for_actives==============================")
    # print(f"====================mentorship_bonus_for_actives==============================")

    for follower in user_tree:
        follower = UsersTreeSerializer(follower)
        follower_id = follower.data.get('invited')['id']

        follower_sum = WarehouseSaleProduct.objects.filter(user__id=follower_id, dateTime__startswith=date).aggregate(
            Sum('summa')
        )

        if follower_sum['summa__sum'] is not None:
            if follower_sum['summa__sum'] / rv_ball["BALL"] >= 50:
                actives += 1
                # print(f"{follower.data.get('invited')=}")

    if actives > 0:
        forMentorship = actives * 31500

    if actives == 3 or actives == 4:
        forMentorship += 66000
    elif actives == 5 or actives == 6:
        forMentorship += 130000
    elif actives == 7 or actives == 8 or actives == 9:
        forMentorship += 210000
    elif actives == 10 or actives == 11 or actives == 12 or actives == 13:
        forMentorship += 330000
    elif actives == 14 or actives == 15 or actives == 16 or actives == 17 or actives == 18:
        forMentorship += 504000
    elif actives >= 19:
        forMentorship += 741000

    # print(f"{forMentorship=}")
    return {"forMentorship": forMentorship}


# def get_user_status(user_id: int, date: str):
#     user_tree = get_user_tree(user_id=user_id).get('tree')[::-1]
#     # followers_statuses = {}
#     user_tree_sum = 0
#
#     user_sum = WarehouseSaleProduct.objects.filter(user__id=user_id, dateTime__startswith=date).aggregate(Sum('summa'))
#     if user_sum['summa__sum'] is not None:
#         user_tree_sum += user_sum['summa__sum']
#         user_summa = user_sum['summa__sum']
#     else:
#         user_summa = 0
#
#     for follower in user_tree:
#         follower_sum = WarehouseSaleProduct.objects.filter(user__id=follower['id'], dateTime__startswith=date).aggregate(Sum('summa'))
#
#         if follower_sum['summa__sum'] is not None:
#             user_tree_sum += follower_sum['summa__sum']
#
#     user_tree_score = user_tree_sum / rv_ball['BALL']
#
#     if user_tree_score >= 500 and user_tree_score < 2000:
#         kvalifikatsiya = "Konsultant"
#     elif user_tree_score >= 2000 and user_tree_score < 7000:
#         kvalifikatsiya = "Menejer"
#     elif user_tree_score >= 7000 and user_tree_score < 15000:
#         kvalifikatsiya = "Menejer Pro"
#     elif user_tree_score >= 15000 and user_tree_score < 40000:
#         kvalifikatsiya = "Supervisor"
#     elif user_tree_score >= 40000 and user_tree_score < 70000:
#         kvalifikatsiya = "Gold"
#     elif user_tree_score >= 70000 and user_tree_score < 100000:
#         kvalifikatsiya = "Platinum"
#     elif user_tree_score >= 100000:
#         kvalifikatsiya = "Diamond"
#     else:
#         kvalifikatsiya = "None"
#
#
#     if user_summa / rv_ball["BALL"] > 50:
#         personal_bonus = (user_summa / rv_ball["BALL"] - 50) * 0.2 * rv_ball["RV"] + 50 * 0.11 * rv_ball['RV']
#     else:
#         personal_bonus = user_summa / rv_ball["BALL"] * 0.11 * rv_ball["RV"]
#
#     if user_summa / rv_ball["BALL"] >= 250:
#         hisobla = ((user_summa / rv_ball["BALL"]) - 50) // 200
#         extra_bonus = int(hisobla) * 300000
#     else:
#         extra_bonus = 0
#
#     return {'user_status': kvalifikatsiya, "user_score": round(user_summa/ rv_ball["BALL"], 2), "user_tree_score": user_tree_score, "user_tree_summa": round(user_tree_sum, 2),
#             "personal_bonus": round(personal_bonus, 2), "extra_bonus": round(extra_bonus, 2)}


def get_user_status_and_team_score(user_id: str, date: str):
    user_tree = get_user_tree(user_id=user_id).get('tree')[::-1]
    user_tree_sum = 0


    user_sum = WarehouseSaleProduct.objects.filter(user__id=user_id, dateTime__startswith=date).aggregate(Sum('summa'))
    if user_sum['summa__sum'] is not None:
        user_tree_sum += user_sum['summa__sum']
        user_summa = user_sum['summa__sum']
    else:
        user_summa = 0

    for follower in user_tree:
        follower_sum = WarehouseSaleProduct.objects.filter(user__id=follower['id'],
                                                           dateTime__startswith=date).aggregate(Sum('summa'))

        if follower_sum['summa__sum'] is not None:
            user_tree_sum += follower_sum['summa__sum']
    user_tree_score = user_tree_sum / rv_ball['BALL']



    if user_tree_score >= 500 and user_tree_score < 2000:
        kvalifikatsiya = KONSULTANT
    elif user_tree_score >= 2000 and user_tree_score < 7000:
        if max(follower_sums) >= 2000:
            while max(follower_sums) >= 2000:
                follower_sums.remove(max(follower_sums))
            user_tree_score = sum(follower_sums)
        else:
            kvalifikatsiya = MENEJER
    elif user_tree_score >= 7000 and user_tree_score < 15000:
        kvalifikatsiya = MENEJER_PRO
    elif user_tree_score >= 15000 and user_tree_score < 40000:
        kvalifikatsiya = SUPERVISOR
    elif user_tree_score >= 40000 and user_tree_score < 70000:
        kvalifikatsiya = GOLD
    elif user_tree_score >= 70000 and user_tree_score < 100000:
        kvalifikatsiya = PLATINUM
    elif user_tree_score >= 100000:
        kvalifikatsiya = DIAMOND
    else:
        kvalifikatsiya = DISTRIBUTER

    return {'user_status': kvalifikatsiya, "user_summa": user_summa,
            "user_score": round(user_summa / rv_ball["BALL"], 2), "user_tree_score": user_tree_score,
            "user_tree_summa": round(user_tree_sum, 2)}


def get_user_status_and_team_score2(user_id: str, date: str):
    user_tree = get_user_tree(user_id=user_id).get('tree')[::-1]
    user_tree_sum = 0

    user_stat = get_user_status_and_team_score(user_id=user_id, date=date)
    user_tree_sum += user_stat['user_summa']
    user_summa = user_stat['user_summa']
    # print(f"{user_stat['user_tree_score']=}")
    # print(f"====================get_user_status_and_team_score2==============================")
    # print(f"====================get_user_status_and_team_score2==============================")
    # print(f"====================get_user_status_and_team_score2==============================")

    for follower in user_tree:
        follower_stat = get_user_status_and_team_score(user_id=follower['id'], date=date)
        # print(f"{follower['first_name']} {follower['last_name']} {follower_stat['user_status']} {follower_stat['user_score']=}")

        if follower_stat['user_status'] == "None":
            # print(f"{follower_stat['user_status']=}         {follower_stat['user_tree_score']=}")
            user_tree_sum += follower_stat['user_summa']
        elif follower_stat['user_status'] != user_stat['user_status'] or (follower_stat['user_status'] == user_stat['user_status'] \
                and (user_stat['user_tree_score'] - follower_stat['user_tree_score']) > follower_stat['user_tree_score']):
            # print(f"{follower_stat['user_status']=}         {follower_stat['user_tree_score']=}")
            user_tree_sum += follower_stat['user_summa']
        else:
            # print(f"{follower=}")
            # print(f"{follower_stat=}")
            user_tree_sum -= follower_stat['user_tree_summa']

    user_tree_score = user_tree_sum / rv_ball['BALL']

    if user_tree_score >= 500 and user_tree_score < 2000:
        kvalifikatsiya = KONSULTANT
    elif user_tree_score >= 2000 and user_tree_score < 7000:
        kvalifikatsiya = MENEJER
    elif user_tree_score >= 7000 and user_tree_score < 15000:
        kvalifikatsiya = MENEJER_PRO
    elif user_tree_score >= 15000 and user_tree_score < 40000:
        kvalifikatsiya = SUPERVISOR
    elif user_tree_score >= 40000 and user_tree_score < 70000:
        kvalifikatsiya = GOLD
    elif user_tree_score >= 70000 and user_tree_score < 100000:
        kvalifikatsiya = PLATINUM
    elif user_tree_score >= 100000:
        kvalifikatsiya = DIAMOND
    else:
        kvalifikatsiya = DISTRIBUTER

    if user_summa / rv_ball["BALL"] > 50:
        personal_bonus = (user_summa / rv_ball["BALL"] - 50) * 0.2 * rv_ball["RV"] + 50 * 0.11 * rv_ball['RV']
    else:
        personal_bonus = user_summa / rv_ball["BALL"] * 0.11 * rv_ball["RV"]

    if user_summa / rv_ball["BALL"] >= 250:
        hisobla = ((user_summa / rv_ball["BALL"]) - 50) // 200
        extra_bonus = int(hisobla) * 300000
    else:
        extra_bonus = 0

    if user_tree_score < 0:
        coupon = user_stat['user_score']
    else:
        coupon = user_tree_score

    # return {'user_status': kvalifikatsiya, "user_score": round(user_summa/ rv_ball["BALL"], 2), "user_tree_score": user_tree_score, "user_tree_summa": round(user_tree_sum, 2),
    #         "personal_bonus": round(personal_bonus, 2), "extra_bonus": round(extra_bonus, 2)}
    return {'user_status': kvalifikatsiya, "user_score": round(user_summa / rv_ball["BALL"], 2),
            "user_tree_score": user_stat['user_tree_score'], "user_tree_summa": round(user_stat['user_tree_summa'], 2),
            "personal_bonus": round(personal_bonus, 2), "extra_bonus": round(extra_bonus, 2), "coupon": coupon}


def mentorship_bonus_for_followers_status(user_id: str, date: str):
    bonus_sum = 0
    followers_status = []
    # user_tree = get_user_tree(user_id=user_id).get('tree')
    user_tree_q = UsersTree.objects.filter(offerer__id=user_id).filter(deleted=False)
    # user_tree = []
    for follower in user_tree_q:
        follower_ser = UsersTreeSerializer(follower)
        # user_tree.append(follower_ser.data['invited'])

        # print(f"====================mentorship_bonus_for_followers_status==============================")
        # print(f"====================mentorship_bonus_for_followers_status==============================")
        # print(f"====================mentorship_bonus_for_followers_status==============================")

        # for follower in user_tree:
        # kvalifikatsiya = get_user_status(user_id=follower['id'], date=date)
        # kvalifikatsiya = get_user_status_and_team_score2(user_id=follower['id'], date=date)
        kvalifikatsiya = get_user_status_and_team_score2(user_id=follower_ser.data['invited']['id'], date=date)

        followers_status.append(kvalifikatsiya['user_status'])
    #     print(f"{follower['first_name']} {follower['last_name']} {kvalifikatsiya['user_status']=}")
    #
    # print(f"{followers_status=}")

    if KONSULTANT in followers_status:
        sanoq = followers_status.count(KONSULTANT)
        if sanoq > 0:
            bonus_sum += sanoq * 50000

    if MENEJER in followers_status:
        sanoq = followers_status.count(MENEJER)
        if sanoq > 0:
            bonus_sum += sanoq * 200000

    if MENEJER_PRO in followers_status:
        sanoq = followers_status.count(MENEJER_PRO)
        if sanoq > 0:
            bonus_sum += sanoq * 700000

    if SUPERVISOR in followers_status:
        sanoq = followers_status.count(SUPERVISOR)
        if sanoq > 0:
            bonus_sum += sanoq * 1500000

    if GOLD in followers_status:
        sanoq = followers_status.count(GOLD)
        if sanoq > 0:
            bonus_sum += sanoq * 4000000

    if PLATINUM in followers_status:
        sanoq = followers_status.count(PLATINUM)
        if sanoq > 0:
            bonus_sum += sanoq * 7000000

    if DIAMOND in followers_status:
        sanoq = followers_status.count(DIAMOND)
        if sanoq > 0:
            bonus_sum += sanoq * 10000000

    return {"bonus_for_followers_status": bonus_sum}


def collective_bonus_amount(user_id: str, date: str, get_user_status_dict: dict):
    bonus_sum = 0
    # datam = get_user_status(user_id=user_id, date=date)
    datam = get_user_status_dict
    statusim = datam["user_status"]

    if statusim == KONSULTANT:
        stat_foiz = 10
    elif statusim == MENEJER:
        stat_foiz = 15
    elif statusim == MENEJER_PRO:
        stat_foiz = 19
    elif statusim == SUPERVISOR:
        stat_foiz = 23
    elif statusim == GOLD:
        stat_foiz = 27
    elif statusim == PLATINUM:
        stat_foiz = 30
    elif statusim == DIAMOND:
        stat_foiz = 33
    else:
        stat_foiz = 0

    bonusim = WarehouseSaleProduct.objects.filter(user__id=user_id, dateTime__startswith=date).aggregate(Sum('summa'))
    if bonusim['summa__sum'] is not None:
        bonus_sum += (bonusim['summa__sum'] / rv_ball['BALL']) * (stat_foiz / 100) * rv_ball["RV"]
    return {"collective_bonus_amount": round(bonus_sum, 2), "stat_percent": stat_foiz}


def collective_bonus_amount2(user_id: str, date: str, collective_bonus_percent: int):
    bonus = 0
    user_tree_q = UsersTree.objects.filter(offerer__id=user_id).filter(deleted=False)
    user_tree = []
    for follower in user_tree_q:
        follower_ser = UsersTreeSerializer(follower)
        user_tree.append(follower_ser.data['invited'])
    # print(f"====================collective_bonus_amount2==============================")
    # print(f"====================collective_bonus_amount2==============================")
    # print(f"====================collective_bonus_amount2==============================")

    for follower in user_tree:
        # kvalifikatsiya = get_user_status(user_id=follower['id'], date=date)
        user_status = get_user_status_and_team_score2(user_id=follower['id'], date=date)
        collective_bonus = collective_bonus_amount(user_id=follower['id'], date=date, get_user_status_dict=user_status)

        if user_status['user_status'] != "None" and collective_bonus_percent > collective_bonus['stat_percent']:
            # print("#############################################")
            # # print(f"{user_status['user_tree_score']=}")
            # print(f"{collective_bonus_percent=}")
            # print(f"{collective_bonus['stat_percent']=}")
            # percent = (100 / (collective_bonus_percent - collective_bonus['stat_percent']))
            # print(f"{percent=}")
            # f_bonus = user_status['user_tree_score'] * ((collective_bonus_percent - collective_bonus['stat_percent']) / 100) * rv_ball["RV"]
            # print(f"{f_bonus=}")

            bonus += user_status['user_tree_score'] * ((collective_bonus_percent - collective_bonus['stat_percent']) / 100) * rv_ball["RV"]



        elif user_status['user_status'] == "None":
            followers_followers = []
            user_follower_tree_q = UsersTree.objects.filter(offerer__id=follower['id']).filter(deleted=False)

            for f in user_follower_tree_q:
                f_ser = UsersTreeSerializer(f)
                followers_followers.append(f_ser.data['invited'])

            while followers_followers != []:
                followers_followers_status = get_user_status_and_team_score2(user_id=followers_followers[0]['id'], date=date)
                followers_followers_collective_bonus = collective_bonus_amount(user_id=followers_followers[0]['id'], date=date, get_user_status_dict=followers_followers_status)

                if followers_followers_status['user_status'] != DISTRIBUTER and collective_bonus_percent > \
                        followers_followers_collective_bonus['stat_percent']:
                    bonus += followers_followers_status['user_tree_score'] * ((collective_bonus_percent - followers_followers_collective_bonus['stat_percent']) / 100) * rv_ball["RV"]

                    followers_followers.pop(0)

                elif user_status['user_status'] == "None":
                    user_follower_tree_q = UsersTree.objects.filter(offerer__id=followers_followers[0]['id']).filter(
                        deleted=False)
                    followers_followers.pop(0)

                    for f in user_follower_tree_q:
                        f_ser = UsersTreeSerializer(f)
                        followers_followers.append(f_ser.data['invited'])

    return {"for_followers_status_percent": round(bonus, 2)}


# def user_all_bonuses(user_id: int, date: str):
#     user = Users.objects.get(id=user_id)
#     user_ser = UsersSerializer(user)
#     bonus_for_actives = mentorship_bonus_for_actives(user_id=user_id, date=date)
#     user_status = get_user_status(user_id=user_id, date=date)
#     bonus_for_followers_status = mentorship_bonus_for_followers_status(user_id=user_id, date=date)
#     collective_bonus = collective_bonus_amount(user_id=user_id, date=date, get_user_status_dict=user_status)
#
#     data = {}
#     data['user'] = user_ser.data
#     data.update(user_status)
#     data.update(bonus_for_actives)
#     data.update(bonus_for_followers_status)
#     data.update(collective_bonus)
#
#     return data

def get_user_salary_warehouse(user: dict, month: str):
    head_warehouse = Warehouse.objects.get(name="Bosh Filial")
    head_warehouse_ser = WarehouseSerializer(head_warehouse).data
    warehouse = {"warehouse": head_warehouse_ser, "products_amount": 0}

    warehouses = Warehouse.objects.all()
    warehouse_ser = WarehouseSerializer(warehouses, many=True).data
    for i in warehouse_ser:
        sales = WarehouseSaleProduct.objects.filter(user__id=user['id'], dateTime__startswith=str(month)[:7], warehouse__id=i['id']).aggregate(Sum('amount'))

        if warehouse['products_amount'] < sales['amount__sum'] if sales['amount__sum'] is not None else 0:
            warehouse = {"warehouse": i, "products_amount": sales['amount__sum'] if sales['amount__sum'] is not None else 0}

    warehouse.pop("products_amount")
    return warehouse


def user_all_bonuses2(user_id: str, date: str):
    date = str(date)[:7]
    if date < "2023-09":
        user = User.objects.get(id=user_id)
        user_ser = ForOthersUsersSerializer(user).data
        # user_teacher = UsersTree.objects.get(invited__id=user_id)
        # user_teacher_ser = UsersTreeSerializer(user_teacher)
        bonus_for_actives = mentorship_bonus_for_actives(user_id=user_id, date=date)
        user_status = get_user_status_and_team_score2(user_id=user_id, date=date)
        bonus_for_followers_status = mentorship_bonus_for_followers_status(user_id=user_id, date=date)
        collective_bonus = collective_bonus_amount(user_id=user_id, date=date, get_user_status_dict=user_status)

        # print(f"====================user_all_bonuses2==============================")
        # print(f"====================user_all_bonuses2==============================")
        # print(f"====================user_all_bonuses2==============================")
        # print(f"{collective_bonus=}")

        collective_bonus2 = collective_bonus_amount2(user_id=user_id, date=date, collective_bonus_percent=collective_bonus['stat_percent'])

        paid = UsersSalaryPayment.objects.filter(user__id=user_id, date__startswith=date).aggregate(Sum('paid'))
        paid = paid['paid__sum'] if paid['paid__sum'] is not None else 0

        # data = {}
        # data['user'] = user_ser.data
        # data['teacher'] = user_teacher_ser.data['offerer']
        # data.update(user_status)
        # data.update(bonus_for_actives)
        # data.update(bonus_for_followers_status)
        # data.update(collective_bonus)
        # data.update(collective_bonus2)

        user_ser.update(user_status)
        user_ser.update(bonus_for_actives)
        user_ser.update(bonus_for_followers_status)
        user_ser.update(collective_bonus)
        user_ser.update(collective_bonus2)

        teacher_sale_sum = WarehouseSaleProduct.objects.filter(user__id=user_id, dateTime__startswith=date).aggregate(Sum('summa'))
        if teacher_sale_sum['summa__sum'] is not None and teacher_sale_sum['summa__sum'] / rv_ball['BALL'] >= 50:
            user_ser['salary'] = collective_bonus['collective_bonus_amount'] + bonus_for_followers_status['bonus_for_followers_status'] + user_status['personal_bonus'] + user_status['extra_bonus'] + \
                             bonus_for_actives["forMentorship"] + collective_bonus2['for_followers_status_percent']
        else:
            # data['salary'] = user_status['personal_bonus'] + user_status['extra_bonus']
            user_ser['salary'] = user_status['personal_bonus'] + user_status['extra_bonus']

        # data['paid'] = paid
        # data['debt'] = data['salary'] - paid
        # data.update(get_user_salary_warehouse(user_ser.data, month=date))

        # if user.user_roles == BRAND_MANAGER:
        #     # brand manager uchun har bir izdoshidan beriluvchi 20.000 ming so'm bonusi
        #     tree_bonus_20s = get_user_tree(user_id)
        #     tree_bonus_20s = len(tree_bonus_20s) * 20000
        #
        #     # shajaradan 5% bonusi hisoblash
        #     percent5_bonus = collective_bonus['collective_bonus_amount'] * (5/100)
        #     user_ser['salary'] += tree_bonus_20s + percent5_bonus

        user_ser['paid'] = paid
        user_ser['debt'] = user_ser['salary'] - paid
        user_ser.update(get_user_salary_warehouse(user_ser, month=date))

        return user_ser
    else:
        user_ser = user_all_bonuses_mp_2_0(user_id=user_id, month=date)
        # user_ser = get_salary_data(user_id=user_id, month=date)
        update_one_user_calculated_salary(month=date, user_id=user_id, salary_info=user_ser)
        return user_ser


def users_all_bonuses_test(date: str):
    # salaries = UserSalary.objects.filter(month__startswith=str(date)[:7])
    # salaries = UserSalary.objects.filter(month__startswith=str(date)[:7], user_score__gt=0)
    salaries = UserSalary.objects.filter(month__startswith=str(date)[:7], user_score__gt=0).order_by("user__last_name")
    salaries_ser = UserSalarySerializerTest(salaries, many=True).data

    salaries_data = []
    for salary_info in salaries_ser:
        data = salary_info.pop("user")
        salary_info.pop("id")
        data.update(salary_info)
        salaries_data.append(data)

    return salaries_data


def user_all_bonuses_test(user_id: str, date: str):
    user = get_object_or_404(User, id=user_id)
    user_ser = ForOthersUsersSerializer(user).data

    try:
        # users = User.objects.filter(auth_status=DONE)
        # for user in users:
        #     if user.id == user_id:

        user_salary = UserSalary.objects.get(user=user, month__startswith=str(date)[:7])
        user_salary_Ser = UserSalarySerializer(user_salary).data

        user_salary_Ser.pop("user")
        user_salary_Ser.pop("id")

        data = {}
        data.update(user_ser)
        data.update(user_salary_Ser)
        data['salary_status'] = True
        # else:
        #     warehouse = Warehouse.objects.get(id="57e06190-7c22-44a0-9b47-2ce314ddd809"),
        #     warehouse = WarehouseSerializer(warehouse).data
        #     data = {
        #         "user_status": "Distributer",
        #         "user_score": 1,
        #         "user_tree_score": 1,
        #         "user_tree_summa": 1,
        #         "personal_bonus": 1,
        #         "extra_bonus": 1,
        #         "coupon": 1,
        #         "forMentorship": 1,
        #         "bonus_for_followers_status": 1,
        #         "collective_bonus_amount": 1,
        #         "stat_percent": 1,
        #         "for_followers_status_percent": 1,
        #         "salary": 1,
        #         "paid": 1,
        #         "debt": 1,
        #         "warehouse": warehouse
        #     }
        return data
    except:
        # warehouse = Warehouse.objects.get(id="57e06190-7c22-44a0-9b47-2ce314ddd809")  # on server
        warehouse = Warehouse.objects.get(id="eafde061-1eae-4233-9ae4-f5381ecf521b")
        warehouse = WarehouseSerializer(warehouse).data
        data = {
                "id": user_ser['id'],
                "first_name": user.first_name,
                "last_name": user.last_name,
                "user_id": user.user_id,
                "phoneNumTwo": user.phoneNumTwo,
                "phone_number": user.phone_number,
                "date": user.date,
                "photo": user_ser['photo'],
                "email": user.email,
                "passport": user.passport,
                "address": user.address,
                "dateOfBirth": user.dateOfBirth,
                "warehouse": warehouse,
                "created_time": user.date,
                "updated_time":  user.date,
                "user_status": "Distributer",
                "user_score": 0,
                "user_tree_score": 0,
                "user_tree_summa": 0,
                "personal_bonus": 0,
                "extra_bonus": 0,
                "coupon": 0,
                "forMentorship": 0,
                "bonus_for_followers_status": 0,
                "collective_bonus_amount": 0,
                "stat_percent": 0,
                "for_followers_status_percent": 0,
                "salary": 0,
                "paid": 0,
                "debt": 0,
                "month": date,
                "salary_status": True
        }
        # data = user_all_bonuses2(user_id=user_id, date=date)
        return data
        # all_calculated_salaries = UserSalary.objects.filter(month__startswith=str(date)[:7])
        # all_calculated_salaries_ser = UserSalarySerializer(all_calculated_salaries, many=True).data
        # raise ValidationError({
        #     "success": True,
        #     "tree": all_calculated_salaries_ser
        # })

def get_all_shajara(user_id: str, month: str):
    if str(month)[:7] < "2023-09":
        users_Data = {}
        avlod_sanoq = 1
        id = [user_id]
        id_2 = []

        while len(id) > 0:
            data_sheets = UsersTree.objects.filter(invited__date__lte=month).filter(offerer__id=id[0]).filter(deleted=False)
            data_sheets_ser = UsersTreeSerializer(data_sheets, many=True).data

            for user_ser in data_sheets_ser:
                if user_ser['offerer']['id'] == id[0]:
                    # user_data = user_all_bonuses2(user_id=user_ser['invited']['id'], date=month)
                    user_data = user_all_bonuses_test(user_id=user_ser['invited']['id'], date=month)
                    if str(avlod_sanoq) in users_Data:
                        users_Data[f"{avlod_sanoq}"].append(user_data)
                    else:
                        users_Data[f"{avlod_sanoq}"] = []
                        users_Data[f"{avlod_sanoq}"].append(user_data)

                    id_2.append(user_ser['invited']['id'])

            id.pop(0)
            if len(id) == 0:
                avlod_sanoq += 1
                id = id_2
                id_2 = []

        return users_Data
    else:
        return get_all_shajara_mp_2_0(user_id=user_id, month=month)



def get_all_shajara2(user_id: str, month: str):
    # m = get_month_info(year_month=month)
    users_Data = []
    avlod_sanoq = 1
    id = [user_id]
    id_2 = []

    while len(id) > 0:
        data_sheets = UsersTree.objects.filter(invited__date__lte=month, offerer__id=id[0], deleted=False)
        data_sheets_ser = UsersTreeSerializer(data_sheets, many=True).data

        for user_ser in data_sheets_ser:
            if user_ser['offerer']['id'] == id[0]:
                # user_data = user_all_bonuses2(user_id=user_ser['invited']['id'], date=month)
                user_data = user_all_bonuses_test(user_id=user_ser['invited']['id'], date=month)
                users_Data.append(user_data)

                id_2.append(user_ser['invited']['id'])

        id.pop(0)
        if len(id) == 0:
            avlod_sanoq += 1
            id = id_2
            id_2 = []

    return users_Data


def data_to_excel(data: list):
    # from openpyxl.workbook import Workbook
    #
    # wb = Workbook()
    #
    # sheet = wb.active
    #
    # for info in data:
    #     step1 = list(info.values())
    #     step2 = step1[:-1]
    #     step2.append(step1[-1]["name"])
    #
    #     sheet.append(tuple(step2))
    #
    # wb.save("./media/pdf_files/warehouses_info.xlsx")
    pass


def update_calculated_salary(month: str):
    # users = User.objects.filter(deleted=False, date__lte=month).order_by("-date")
    users = User.objects.filter(deleted=False, auth_status=DONE).order_by("-date")
    # users_actives = []
    counter = 0
    for user in users:
        if WarehouseSaleProduct.objects.filter(user=user, dateTime__startswith=str(month)[:7]).exists():
            # users_actives.append(user)
            counter += 1
    # for user in users_actives:
            salary_info = user_all_bonuses2(user_id=user.id, date=month)
            warehouse = Warehouse.objects.get(id=salary_info['warehouse']['id'])
            try:
                calculated = UserSalary.objects.get(user__id=user.id, month__startswith=str(month)[:7])

                calculated.user_status = salary_info['user_status'] if str(salary_info['user_status']) != "None" else "Distributer"
                calculated.user_score = int(salary_info['user_score'])
                calculated.user_tree_score = int(salary_info['user_tree_score'])
                calculated.user_tree_summa = int(salary_info['user_tree_summa'])
                calculated.personal_bonus = int(salary_info['personal_bonus'])
                calculated.extra_bonus = int(salary_info['extra_bonus'])
                calculated.coupon =  int(salary_info['coupon']) if str(month) < "2023-11" else 0
                calculated.forMentorship = int(salary_info['forMentorship'])
                calculated.bonus_for_followers_status = int(salary_info['bonus_for_followers_status'])
                calculated.collective_bonus_amount = int(salary_info['collective_bonus_amount'])
                calculated.stat_percent = int(salary_info['stat_percent'])
                calculated.for_followers_status_percent = int(salary_info['for_followers_status_percent'])
                calculated.salary = int(salary_info['salary'])
                calculated.paid = int(salary_info['paid'])
                calculated.debt = int(salary_info['debt'])
                calculated.warehouse = warehouse
                calculated.save()
            except:
                user = User.objects.get(id=user.id)

                UserSalary.objects.create(
                    user=user,
                    user_status=salary_info['user_status'] if str(salary_info['user_status']) != "None" else "Distributer",
                    user_score=int(salary_info['user_score']),
                    user_tree_score=int(salary_info['user_tree_score']),
                    user_tree_summa=int(salary_info['user_tree_summa']),
                    personal_bonus=int(salary_info['personal_bonus']),
                    extra_bonus=int(salary_info['extra_bonus']),
                    coupon= int(salary_info['coupon']) if str(month) < "2023-11" else 0,
                    forMentorship=int(salary_info['forMentorship']),
                    bonus_for_followers_status=int(salary_info['bonus_for_followers_status']),
                    collective_bonus_amount=int(salary_info['collective_bonus_amount']),
                    stat_percent=int(salary_info['stat_percent']),
                    for_followers_status_percent=int(salary_info['for_followers_status_percent']),
                    salary=int(salary_info['salary']),
                    paid=int(salary_info['paid']),
                    debt=int(salary_info['debt']),
                    warehouse=warehouse,
                    month=month
                )
            if str(month)[:7] > "2023-10" and str(datetime.today().date().day) == "1":
                calculate_user_bonus_account(data={"status": salary_info['user_status'], "id": salary_info['id'], "month": month})

    return {"success": True, "counter": counter}


def update_one_user_calculated_salary(month: str, user_id: str, salary_info: dict):
    # salary_info = user_all_bonuses2(user_id=user_id, date=month)
    warehouse = Warehouse.objects.get(id=salary_info['warehouse']['id'])
    try:
        calculated = UserSalary.objects.get(user__id=user_id, month__startswith=str(month)[:7])
        calculated.user_status = salary_info['user_status'] if str(salary_info['user_status']) != "None" else "Distributer"
        calculated.user_score = int(salary_info['user_score'])
        calculated.user_tree_score = int(salary_info['user_tree_score'])
        calculated.user_tree_summa = int(salary_info['user_tree_summa'])
        calculated.personal_bonus = int(salary_info['personal_bonus'])
        calculated.extra_bonus = int(salary_info['extra_bonus'])
        calculated.coupon =  int(salary_info['coupon']) if str(month) < "2023-11" else 0
        calculated.forMentorship = int(salary_info['forMentorship'])
        calculated.bonus_for_followers_status = int(salary_info['bonus_for_followers_status'])
        calculated.collective_bonus_amount = int(salary_info['collective_bonus_amount'])
        calculated.stat_percent = int(salary_info['stat_percent'])
        calculated.for_followers_status_percent = int(salary_info['for_followers_status_percent'])
        calculated.salary = int(salary_info['salary'])
        calculated.paid = int(salary_info['paid'])
        calculated.debt = int(salary_info['debt'])
        calculated.warehouse = warehouse
        calculated.save()
    except:
        user = User.objects.get(id=user_id)

        UserSalary.objects.create(
            user=user,
            user_status=salary_info['user_status'] if str(salary_info['user_status']) != "None" else "Distributer",
            user_score=int(salary_info['user_score']),
            user_tree_score=int(salary_info['user_tree_score']),
            user_tree_summa=int(salary_info['user_tree_summa']),
            personal_bonus=int(salary_info['personal_bonus']),
            extra_bonus=int(salary_info['extra_bonus']),
            coupon= int(salary_info['coupon']) if str(month) < "2023-11" else 0,
            forMentorship=int(salary_info['forMentorship']),
            bonus_for_followers_status=int(salary_info['bonus_for_followers_status']),
            collective_bonus_amount=int(salary_info['collective_bonus_amount']),
            stat_percent=int(salary_info['stat_percent']),
            for_followers_status_percent=int(salary_info['for_followers_status_percent']),
            salary=int(salary_info['salary']),
            paid=int(salary_info['paid']),
            debt=int(salary_info['debt']),
            warehouse=warehouse,
            month=f"{month}-01"
        )
    if str(month)[:7] > "2023-10" and str(datetime.today().date().day) == "1":
        calculate_user_bonus_account(data={"status": salary_info['user_status'], "id": salary_info['id'], "month": month})

    return {"success": True}


def create_salary_calculate(month: str):
    # users = User.objects.filter(deleted=False, date__lte=month).order_by("-date")
    users = User.objects.filter(deleted=False, auth_status=DONE).order_by("-date")
    # users_actives = []

    for user in users:
        if WarehouseSaleProduct.objects.filter(user=user, dateTime__startswith=str(month)[:7]).exists():
            # users_actives.append(user)

    # for user in users_actives:
            salary_info = user_all_bonuses2(user_id=user.id, date=month)
            warehouse = Warehouse.objects.get(id=salary_info['warehouse']['id'])
            user = User.objects.get(id=salary_info['id'])

            UserSalary.objects.create(
                user=user,
                user_status=salary_info['user_status'] if str(salary_info['user_status']) != "None" else "Distributer",
                user_score=int(salary_info['user_score']),
                user_tree_score=int(salary_info['user_tree_score']),
                user_tree_summa=int(salary_info['user_tree_summa']),
                personal_bonus=int(salary_info['personal_bonus']),
                extra_bonus=int(salary_info['extra_bonus']),
                coupon=int(salary_info['coupon']) if str(month) < "2023-11" else 0,
                forMentorship=int(salary_info['forMentorship']),
                bonus_for_followers_status=int(salary_info['bonus_for_followers_status']),
                collective_bonus_amount=int(salary_info['collective_bonus_amount']),
                stat_percent=int(salary_info['stat_percent']),
                for_followers_status_percent=int(salary_info['for_followers_status_percent']),
                salary=int(salary_info['salary']),
                paid=int(salary_info['paid']),
                debt=int(salary_info['debt']),
                warehouse=warehouse,
                month=month
            )
            if str(month)[:7] > "2023-10" and str(datetime.today().date().day) == "1":
                calculate_user_bonus_account(data={"status": salary_info['user_status'], "id": salary_info['id'], "month": month})

    return {"success": True}


def get_month_info(year_month: str):
    import datetime
    month = str(year_month)
    # initializing date
    test_date = datetime.datetime(int(month[:4]), int(month[5:7]), 4)

    # getting next month
    # using replace to get to last day + offset
    # to reach next month
    nxt_mnth = test_date.replace(day=28) + datetime.timedelta(days=4)

    # subtracting the days from next month date to
    # get last date of current Month
    res = nxt_mnth - datetime.timedelta(days=nxt_mnth.day)
    stat_time = "T05:00:00+05:00"

    return month + "-" + str(res.day) + stat_time


from datetime import datetime, timedelta


def get_first_date_of_next_month(given_month):
    given_month = datetime.strptime(given_month, '%Y-%m')
    next_month = given_month.replace(day=1) + timedelta(days=32)
    first_date_of_next_month = next_month.replace(day=1)
    return first_date_of_next_month


def get_shajara_by_family_tree(user_id: str, month: str):
    month = str(month)[:7]
    user = User.objects.get(id=user_id)
    # if user.auth_status == DONE:
    sales = WarehouseSaleProduct.objects.filter(user__id=user_id, dateTime__startswith=month).aggregate(Sum('summa'))
    user_score = sales["summa__sum"] / rv_ball["BALL"] if sales["summa__sum"] is not None else 0
    tree_score = 0
    tree = []
    family_tree = {
        "user": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_id": user.user_id,
            "user_score": user_score,
            "tree_score": 0,
        },
        "tree": tree
    }
    first_tree = UsersTree.objects.filter(offerer__id=user_id, date__lt=get_first_date_of_next_month(given_month=month))
    if len(first_tree) > 0:
        for follower in first_tree:
            follower_family_tree = get_shajara_by_family_tree(user_id=follower.invited.id, month=month)
            tree.append(follower_family_tree)
            tree_score += follower_family_tree['user']['tree_score']
            # salary = UserSalary.objects.filter(month__startswith=month, user=follower.invited)
            # if len(salary) > 0:
            #     tree_score += float(salary[0].user_tree_score)
        family_tree['user']['tree_score'] = tree_score + user_score
        return family_tree
    else:
        family_tree['user']['tree_score'] = tree_score + user_score
        return family_tree
    # else:
    #     return
