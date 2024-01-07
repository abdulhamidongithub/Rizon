from django.db.models import Sum
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import ModelSerializer
from warehouses.serializers import WarehouseSerializer
from others.rv_ball import rv_ball
from users.models import *
from users.serializers import UsersTreeSerializer, ForOthersUsersSerializer
from warehouses.models import WarehouseSaleProduct, Warehouse

STATUSES = {
    500: "Kosultant",
    2000: "Menejer",
    7000: "Menejer Pro",
    15000: "Supervisor",
    40000: "Gold",
    70000: "Platinum",
    100000: "Diamond"
}

def personal_bonus(user_id: str, month: str):
    month = str(month)[:7]
    sales = WarehouseSaleProduct.objects.filter(user__id=user_id, dateTime__startswith=month).aggregate(Sum('summa'))
    sales_summa = sales['summa__sum'] if sales['summa__sum'] is not None else 0
    if sales_summa != 0:
        return sales_summa / rv_ball["BALL"] * 0.4 * rv_ball["RV"]
    else:
        return 0



def first_tree_bonus_15_percent(user_id: str, month: str):
    month = str(month)[:7]
    user_first_tree = UsersTree.objects.filter(offerer__id=user_id).filter(deleted=False)
    bonus = 0

    for follower in user_first_tree:
        sales = WarehouseSaleProduct.objects.filter(user=follower.invited, dateTime__startswith=month).aggregate(Sum('summa'))
        if sales['summa__sum'] is not None:
            bonus += sales['summa__sum'] / rv_ball["BALL"] * 0.15 * rv_ball["RV"]

    return {"forMentorship": bonus}


class UserSalarySerializer(ModelSerializer):
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


def get_user_tree(user_id: str, month: str):
    month = str(month)[:7]
    tree = []
    id = [str(user_id)]

    sanoq = 1
    while len(id) > 0:
        sanoq += 1
        # user_tree1 = UsersTree.objects.filter(offerer__id=id[0], date__startswith=month).filter(deleted=False)
        user_tree1 = UsersTree.objects.filter(offerer__id=id[0]).filter(deleted=False)

        for follower in user_tree1:
            user = UsersTreeSerializer(follower)
            tree.append(user.data['invited'])
            id.append(str(user.data['invited']['id']))

        id.pop(0)
    return {"tree": tree}


def get_brand_m_user_tree(user_id: str, month: str):
    month = str(month)[:7]
    tree = []
    id = [str(user_id)]

    sanoq = 1
    while len(id) > 0:
        sanoq += 1
        # user_tree1 = UsersTree.objects.filter(offerer__id=id[0], date_startswith=month).filter(deleted=False)
        user_tree1 = UsersTree.objects.filter(offerer__id=id[0]).filter(deleted=False)

        for follower in user_tree1:
            sales = WarehouseSaleProduct.objects.filter(user=follower.invited, dateTime__startswith=month).aggregate(Sum('summa'))
            if sales['summa__sum'] is not None:
                if sales['summa__sum'] > 750000:
                    user = UsersTreeSerializer(follower)
                    tree.append(user.data['invited'])
                    id.append(str(user.data['invited']['id']))

        id.pop(0)
    return {"tree": tree}


def get_user_status_and_team_score(user_id: str, month: str):
    month = str(month)[:7]
    user_tree = get_user_tree(user_id=user_id, month=month).get('tree')[::-1]
    user_tree_sum = 0

    follower_scores = []
    tree_score = 0

    user_sum = WarehouseSaleProduct.objects.filter(user__id=user_id, dateTime__startswith=month).aggregate(Sum('summa'))
    user_summa = user_sum['summa__sum'] if user_sum['summa__sum'] is not None else 0
    user_tree_sum += user_summa

    user_own_score = user_summa / rv_ball['BALL']
    tree_score += user_own_score
    follower_scores.append(user_own_score)

    for follower in user_tree:
        follower_sum = WarehouseSaleProduct.objects.filter(user__id=follower['id'],
                                                           dateTime__startswith=month).aggregate(Sum('summa'))
        follower_summa = follower_sum['summa__sum'] if follower_sum['summa__sum'] is not None else 0
        user_tree_sum += follower_summa

        temp_user_score = follower_summa / rv_ball['BALL']
        follower_scores.append(temp_user_score)
        tree_score += temp_user_score

    if user_tree_sum != 0:
        user_tree_score = user_tree_sum / rv_ball['BALL']
    else:
        user_tree_score = 0

    user_score = user_summa / rv_ball["BALL"] if user_summa != 0 else 0

    if tree_score >= 500 and tree_score < 2000:
        while max(follower_scores) >= 500:
            follower_scores.remove(max(follower_scores))
        if sum(follower_scores) < 500:
            kvalifikatsiya = "None"
        else:
            kvalifikatsiya = "Konsultant"
    elif tree_score >= 2000 and tree_score < 7000:
        while max(follower_scores) >= 2000:
            follower_scores.remove(max(follower_scores))
        if sum(follower_scores) < 2000:
            while max(follower_scores) >= 500:
                follower_scores.remove(max(follower_scores))
            if sum(follower_scores) < 500:
                kvalifikatsiya = "None"
            else:
                kvalifikatsiya = "Konsultant"
        else:
            kvalifikatsiya = "Menejer"
    elif tree_score >= 7000 and tree_score < 15000:
        while max(follower_scores) >= 7000:
            follower_scores.remove(max(follower_scores))
        if sum(follower_scores) < 7000:
            while max(follower_scores) >= 2000:
                follower_scores.remove(max(follower_scores))
            if sum(follower_scores) < 2000:
                while max(follower_scores) >= 500:
                    follower_scores.remove(max(follower_scores))
                if sum(follower_scores) < 500:
                    kvalifikatsiya = "None"
                else:
                    kvalifikatsiya = "Konsultant"
            else:
                kvalifikatsiya = "Menejer"
        else:
            kvalifikatsiya = "Menejer Pro"
    elif tree_score >= 15000 and tree_score < 40000:
        while max(follower_scores) >= 15000:
            follower_scores.remove(max(follower_scores))
        if sum(follower_scores) < 15000:
            while max(follower_scores) >= 7000:
                follower_scores.remove(max(follower_scores))
            if sum(follower_scores) < 7000:
                while max(follower_scores) >= 2000:
                    follower_scores.remove(max(follower_scores))
                if sum(follower_scores) < 2000:
                    while max(follower_scores) >= 500:
                        follower_scores.remove(max(follower_scores))
                    if sum(follower_scores) < 500:
                        kvalifikatsiya = "None"
                    else:
                        kvalifikatsiya = "Konsultant"
                else:
                    kvalifikatsiya = "Menejer"
            else:
                kvalifikatsiya = "Menejer Pro"
        else:
            kvalifikatsiya = "Supervisor"
    elif tree_score >= 40000 and tree_score < 70000:
        while max(follower_scores) >= 40000:
            follower_scores.remove(max(follower_scores))
        if sum(follower_scores) < 40000:
            while max(follower_scores) >= 15000:
                follower_scores.remove(max(follower_scores))
            if sum(follower_scores) < 15000:
                while max(follower_scores) >= 7000:
                    follower_scores.remove(max(follower_scores))
                if sum(follower_scores) < 7000:
                    while max(follower_scores) >= 2000:
                        follower_scores.remove(max(follower_scores))
                    if sum(follower_scores) < 2000:
                        while max(follower_scores) >= 500:
                            follower_scores.remove(max(follower_scores))
                        if sum(follower_scores) < 500:
                            kvalifikatsiya = "None"
                        else:
                            kvalifikatsiya = "Konsultant"
                    else:
                        kvalifikatsiya = "Menejer"
                else:
                    kvalifikatsiya = "Menejer Pro"
            else:
                kvalifikatsiya = "Supervisor"
        else:
            kvalifikatsiya = "Gold"
    elif tree_score >= 70000 and tree_score < 100000:
        while max(follower_scores) >= 70000:
            follower_scores.remove(max(follower_scores))
        if sum(follower_scores) < 70000:
            while max(follower_scores) >= 40000:
                follower_scores.remove(max(follower_scores))
            if sum(follower_scores) < 40000:
                while max(follower_scores) >= 15000:
                    follower_scores.remove(max(follower_scores))
                if sum(follower_scores) < 15000:
                    while max(follower_scores) >= 7000:
                        follower_scores.remove(max(follower_scores))
                    if sum(follower_scores) < 7000:
                        while max(follower_scores) >= 2000:
                            follower_scores.remove(max(follower_scores))
                        if sum(follower_scores) < 2000:
                            while max(follower_scores) >= 500:
                                follower_scores.remove(max(follower_scores))
                            if sum(follower_scores) < 500:
                                kvalifikatsiya = "None"
                            else:
                                kvalifikatsiya = "Konsultant"
                        else:
                            kvalifikatsiya = "Menejer"
                    else:
                        kvalifikatsiya = "Menejer Pro"
                else:
                    kvalifikatsiya = "Supervisor"
            else:
                kvalifikatsiya = "Gold"
        else:
            kvalifikatsiya = "Platinum"
    elif tree_score >= 100000:
        while max(follower_scores) >= 100000:
            follower_scores.remove(max(follower_scores))
        if sum(follower_scores) < 100000:
            while max(follower_scores) >= 70000:
                follower_scores.remove(max(follower_scores))
            if sum(follower_scores) < 70000:
                while max(follower_scores) >= 40000:
                    follower_scores.remove(max(follower_scores))
                if sum(follower_scores) < 40000:
                    while max(follower_scores) >= 15000:
                        follower_scores.remove(max(follower_scores))
                    if sum(follower_scores) < 15000:
                        while max(follower_scores) >= 7000:
                            follower_scores.remove(max(follower_scores))
                        if sum(follower_scores) < 7000:
                            while max(follower_scores) >= 2000:
                                follower_scores.remove(max(follower_scores))
                            if sum(follower_scores) < 2000:
                                while max(follower_scores) >= 500:
                                    follower_scores.remove(max(follower_scores))
                                if sum(follower_scores) < 500:
                                    kvalifikatsiya = "None"
                                else:
                                    kvalifikatsiya = "Konsultant"
                            else:
                                kvalifikatsiya = "Menejer"
                        else:
                            kvalifikatsiya = "Menejer Pro"
                    else:
                        kvalifikatsiya = "Supervisor"
                else:
                    kvalifikatsiya = "Gold"
            else:
                kvalifikatsiya = "Platinum"
        else:
            kvalifikatsiya = "Diamond"
    else:
        kvalifikatsiya = "None"

    # user_tree_score = sum(follower_scores)
    user_score = user_own_score

    return {'user_status': kvalifikatsiya, "user_summa": user_summa,
            "user_score": round(user_score, 2), "user_tree_score": user_tree_score,
            "user_tree_summa": round(user_tree_sum, 2)}

def get_user_status_and_team_score2(user_id: str, month: str):
    month = str(month)[:7]
    user_tree = get_user_tree(user_id=user_id, month=month).get('tree')[::-1]
    # user_tree = UsersTree.objects.filter(offerer__id=user_id).filter(deleted=False)
    user_tree_sum = 0


    user_stat = get_user_status_and_team_score(user_id=user_id, month=month)
    user_tree_sum += user_stat['user_summa']
    user_summa = user_stat['user_summa']

    for follower in user_tree:
        follower_stat = get_user_status_and_team_score(user_id=follower['id'], month=month)
        # follower_stat = get_user_status_and_team_score(user_id=follower.invited.id, month=month)

        if follower_stat['user_status'] == "None":
            user_tree_sum += follower_stat['user_summa']
        elif follower_stat['user_status'] != user_stat['user_status'] or follower_stat['user_status'] == user_stat['user_status'] \
                and (user_stat['user_tree_score'] - follower_stat['user_tree_score']) > follower_stat['user_tree_score']:
            user_tree_sum += follower_stat['user_summa']
        else:
            user_tree_sum -= follower_stat['user_tree_summa']
            # user_tree_sum += follower_stat['user_summa']  + follower_stat['user_score']
        print(f"Stat: {follower_stat}, {user_tree_sum}")

    if user_tree_sum > 0:
        user_tree_score = user_tree_sum / rv_ball['BALL']
    else:
        user_tree_score = 0

    if user_tree_score >= 500 and user_tree_score < 2000:
        kvalifikatsiya = "Konsultant"
    elif user_tree_score >= 2000 and user_tree_score < 7000:
        kvalifikatsiya = "Menejer"
    elif user_tree_score >= 7000 and user_tree_score < 15000:
        kvalifikatsiya = "Menejer Pro"
    elif user_tree_score >= 15000 and user_tree_score < 40000:
        kvalifikatsiya = "Supervisor"
    elif user_tree_score >= 40000 and user_tree_score < 70000:
        kvalifikatsiya = "Gold"
    elif user_tree_score >= 70000 and user_tree_score < 100000:
        kvalifikatsiya = "Platinum"
    elif user_tree_score >= 100000:
        kvalifikatsiya = "Diamond"
    else:
        kvalifikatsiya = "None"

    user_score = user_summa / rv_ball["BALL"] if user_summa != 0 else 0
    p_bonus = user_score * 0.4 * rv_ball["RV"] if user_score != 0 else 0

    # if user_score >= 250:
    #     hisobla = ((user_summa / rv_ball["BALL"]) - 50) // 200
    #     extra_bonus = int(hisobla) * 300000
    # else:
    #     extra_bonus = 0

    # if user_tree_score < 0:
    #     coupon = user_stat['user_score']
    # else:
    #     coupon = user_tree_score

    return {'user_status': kvalifikatsiya, "user_score": round(user_score, 2),
            "user_tree_score": user_stat['user_tree_score'], "user_tree_summa": round(user_stat['user_tree_summa'], 2),
            "personal_bonus": round(p_bonus, 2),
            "extra_bonus": 0, "coupon": 0}


def mentorship_bonus_for_followers_status(user_id: str, month: str):
    month = str(month)[:7]
    bonus_sum = 0
    followers_status = []
    user_tree_q = UsersTree.objects.filter(offerer__id=user_id).filter(deleted=False)

    for follower in user_tree_q:
        kvalifikatsiya = get_user_status_and_team_score2(user_id=follower.invited.id, month=month)
        followers_status.append(kvalifikatsiya['user_status'])

    if "Konsultant" in followers_status:
        sanoq = followers_status.count("Konsultant")
        if sanoq > 0:
            bonus_sum += sanoq * 50000

    if "Menejer" in followers_status:
        sanoq = followers_status.count("Menejer")
        if sanoq > 0:
            bonus_sum += sanoq * 200000

    if "Menejer Pro" in followers_status:
        sanoq = followers_status.count("Menejer Pro")
        if sanoq > 0:
            bonus_sum += sanoq * 700000

    if "Supervisor" in followers_status:
        sanoq = followers_status.count("Supervisor")
        if sanoq > 0:
            bonus_sum += sanoq * 1500000

    if "Gold" in followers_status:
        sanoq = followers_status.count("Gold")
        if sanoq > 0:
            bonus_sum += sanoq * 4000000

    if "Platinum" in followers_status:
        sanoq = followers_status.count("Platinum")
        if sanoq > 0:
            bonus_sum += sanoq * 7000000

    if "Diamond" in followers_status:
        sanoq = followers_status.count("Diamond")
        if sanoq > 0:
            bonus_sum += sanoq * 10000000

    return {"bonus_for_followers_status": bonus_sum}


def collective_bonus_amount(user_id: str, month: str, get_user_status_dict: dict):
    month = str(month)[:7]
    bonus_sum = 0
    datam = get_user_status_dict
    statusim = datam["user_status"]

    if statusim == "Konsultant":
        stat_foiz = 10
    elif statusim == "Menejer":
        stat_foiz = 15
    elif statusim == "Menejer Pro":
        stat_foiz = 19
    elif statusim == "Supervisor":
        stat_foiz = 23
    elif statusim == "Gold":
        stat_foiz = 27
    elif statusim == "Platinum":
        stat_foiz = 30
    elif statusim == "Diamond":
        stat_foiz = 33
    else:
        stat_foiz = 0

    bonusim = WarehouseSaleProduct.objects.filter(user__id=user_id, dateTime__startswith=month).aggregate(Sum('summa'))
    if bonusim['summa__sum'] is not None:
        bonus_sum += (bonusim['summa__sum'] / rv_ball['BALL']) * (stat_foiz / 100) * rv_ball["RV"]
    return {"collective_bonus_amount": round(bonus_sum, 2), "stat_percent": stat_foiz}


def collective_bonus_amount2(user_id: str, month: str, collective_bonus_percent: int):
    month = str(month)[:7]
    bonus = 0
    user_tree_q = UsersTree.objects.filter(offerer__id=user_id).filter(deleted=False)
    user_tree = []
    for follower in user_tree_q:
        follower_ser = UsersTreeSerializer(follower)
        user_tree.append(follower_ser.data['invited'])

    for follower in user_tree:
        user_status = get_user_status_and_team_score2(user_id=follower['id'], month=month)
        collective_bonus = collective_bonus_amount(user_id=follower['id'], month=month, get_user_status_dict=user_status)

        if user_status['user_status'] != "None" and collective_bonus_percent > collective_bonus['stat_percent']:
            bonus += user_status['user_tree_score'] * ((collective_bonus_percent - collective_bonus['stat_percent']) / 100) * rv_ball["RV"]

        elif user_status['user_status'] == "None":
            followers_followers = [{"id": follower['id']}]
            user_follower_tree_q = UsersTree.objects.filter(offerer__id=follower['id']).filter(deleted=False)

            for f in user_follower_tree_q:
                f_ser = UsersTreeSerializer(f)
                followers_followers.append(f_ser.data['invited'])

            while followers_followers != []:
                followers_followers_status = get_user_status_and_team_score2(user_id=followers_followers[0]['id'], month=month)
                followers_followers_collective_bonus = collective_bonus_amount(user_id=followers_followers[0]['id'], month=month, get_user_status_dict=followers_followers_status)

                if followers_followers_status['user_status'] != "None" and collective_bonus_percent > \
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


def collective_bonus_amount_test(user_id: str, month: str, collective_bonus_percent: int):
    month = str(month)[:7]
    bonus = 0
    user_tree_q = UsersTree.objects.filter(offerer__id=user_id).filter(deleted=False)
    user_tree = []
    for follower in user_tree_q:
        follower_ser = UsersTreeSerializer(follower)
        user_tree.append(follower_ser.data['invited'])

    for follower in user_tree:
        user_status = get_user_status_and_team_score2(user_id=follower['id'], month=month)
        collective_bonus = collective_bonus_amount(user_id=follower['id'], month=month, get_user_status_dict=user_status)

        if user_status['user_status'] == "None":
            # bonus += user_status['user_tree_score'] * ((collective_bonus_percent - collective_bonus['stat_percent']) / 100) * rv_ball["RV"]
            bonus += user_status['user_tree_score'] * (collective_bonus_percent / 100) * rv_ball['RV']

        elif collective_bonus['stat_percent'] < collective_bonus_percent:
            bonus += user_status['user_tree_score'] * ((collective_bonus_percent - collective_bonus['stat_percent']) / 100) * rv_ball['RV']

    return {"for_followers_status_percent": round(bonus, 2)}


def get_user_salary_warehouse(user: dict, month: str):
    month = str(month)[:7]
    # head_warehouse = Warehouse.objects.get(id="57e06190-7c22-44a0-9b47-2ce314ddd809")  # on server
    head_warehouse = Warehouse.objects.get(id="eafde061-1eae-4233-9ae4-f5381ecf521b")
    head_warehouse_ser = WarehouseSerializer(head_warehouse).data
    warehouse = {"warehouse": head_warehouse_ser, "products_amount": 0}

    warehouses = Warehouse.objects.all()
    warehouse_ser = WarehouseSerializer(warehouses, many=True).data
    for i in warehouse_ser:
        sales = WarehouseSaleProduct.objects.filter(user__id=user['id'], dateTime__startswith=str(month)[:7], warehouse__id=i['id']).aggregate(Sum('amount'))

        sales_amount = sales['amount__sum'] if sales['amount__sum'] is not None else 0
        if warehouse['products_amount'] < sales_amount:
            warehouse = {"warehouse": i, "products_amount": sales_amount}

    warehouse.pop("products_amount")
    return warehouse



def user_all_bonuses_mp_2_0(user_id: str, month: str):
    month = str(month)[:7]
    user = User.objects.get(id=user_id)
    user_ser = ForOthersUsersSerializer(user).data

    bonus_for_actives = first_tree_bonus_15_percent(user_id=user_id, month=month)
    user_status = get_user_status_and_team_score2(user_id=user_id, month=month)
    bonus_for_followers_status = mentorship_bonus_for_followers_status(user_id=user_id, month=month)
    collective_bonus = collective_bonus_amount(user_id=user_id, month=month, get_user_status_dict=user_status)
    # collective_bonus2 = collective_bonus_amount_test(user_id=user_id, month=month, collective_bonus_percent=collective_bonus['stat_percent'])
    collective_bonus2 = collective_bonus_amount2(user_id=user_id, month=month, collective_bonus_percent=collective_bonus['stat_percent'])

    paid = UsersSalaryPayment.objects.filter(user__id=user_id, date__startswith=month).aggregate(Sum('paid'))
    paid = paid['paid__sum'] if paid['paid__sum'] is not None else 0

    user_ser.update(user_status)
    user_ser.update(bonus_for_actives)
    user_ser.update(bonus_for_followers_status)
    user_ser.update(collective_bonus)
    user_ser.update(collective_bonus2)

    teacher_sale_sum = WarehouseSaleProduct.objects.filter(user__id=user_id, dateTime__startswith=month).aggregate(Sum('summa'))
    if teacher_sale_sum['summa__sum'] is not None and teacher_sale_sum['summa__sum'] / rv_ball['BALL'] >= 50:
        user_ser['salary'] = collective_bonus['collective_bonus_amount'] + bonus_for_followers_status['bonus_for_followers_status'] + user_status['personal_bonus'] + user_status['extra_bonus'] + \
                         bonus_for_actives['forMentorship'] + collective_bonus2['for_followers_status_percent']
    else:
        user_ser['salary'] = user_status['personal_bonus'] + user_status['extra_bonus']

    if user.user_roles == BRAND_MANAGER:
        # brand manager uchun har bir izdoshidan beriluvchi 20.000 ming so'm bonusi
        tree_bonus_20s = get_brand_m_user_tree(user_id, month=month)
        tree_bonus_20s = len(tree_bonus_20s['tree']) * 20000

        # shajaradan 5% bonusi hisoblash
        percent5_bonus = collective_bonus['collective_bonus_amount'] * (5/100)
        user_ser['salary'] += tree_bonus_20s + percent5_bonus

    user_ser['paid'] = paid
    user_ser['debt'] = user_ser['salary'] - paid
    user_ser.update(get_user_salary_warehouse(user_ser, month=month))

    return user_ser


def user_all_bonuses_test(user_id: str, month: str):
    month = str(month)[:7]
    user = get_object_or_404(User, id=user_id)
    user_ser = ForOthersUsersSerializer(user).data

    try:
        user_salary = UserSalary.objects.get(user=user, month__startswith=str(month)[:7])
        user_salary_Ser = UserSalarySerializer(user_salary).data

        user_salary_Ser.pop("user")
        user_salary_Ser.pop("id")

        data = {}
        data.update(user_ser)
        data.update(user_salary_Ser)
        data['salary_status'] = True
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
                "month": month,
                "salary_status": True
        }
        return data


def get_all_shajara_mp_2_0(user_id: str, month: str):
    month = str(month)[:7]
    users_Data = {}
    avlod_sanoq = 1
    id = [user_id]
    id_2 = []

    # from datetime import datetime
    # sana = str(datetime.today())[:19]
    # daqiqa = sana.find(":")
    # soat = sana[11:sana.find(":")]
    #
    # soat_pl = int(soat) + 5
    # if soat_pl > 23:
    #     soat_plus = soat_pl - 24
    # else:
    #     soat_plus = soat_pl


    while len(id) > 0:
        # data_sheets = UsersTree.objects.filter(invited__date__lte=f"{month}-01 {soat_plus}{sana[daqiqa:]}").filter(offerer__id=id[0]).filter(deleted=False)
        data_sheets = UsersTree.objects.filter(offerer__id=id[0]).filter(deleted=False)
        data_sheets_ser = UsersTreeSerializer(data_sheets, many=True).data

        for user_ser in data_sheets_ser:
            if user_ser['offerer']['id'] == id[0]:
                user_data = user_all_bonuses_test(user_id=user_ser['invited']['id'], month=month)
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
