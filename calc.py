
list1 = [51616, 47447, 46216, 45087, 42056, 39467, 17662, 8831, 114803]
list2 = [46923, 43140, 42020, 40991, 38236, 35886, 14588, 7294, 94822]

states_list1 = ["ANDAMAN and NICOBAR ISLANDS", "ARUNACHAL PRADESH", "ASSAM", "HIMACHAL PRADESH", "JAMMU and KASHMIR",
                    "LADAKH", "LAKSHADWEEP", "MANIPUR", "MEGHALAYA", "MIZORAM", "NAGALAND", "SIKKIM", "TRIPURA", "UTTARAKHAND"]

states_list2 = ["ANDHRA PRADESH", "BIHAR", "CHANDIGARH", "CHHATTISGARH", "GOA", "GUJARAT", "HARYANA", "JHARKHAND",
                    "KARNATAKA", "KERALA", "MADHYA PRADESH", "MAHARASHTRA", "NCT OF DELHI", "ORISSA", "PUDUCHERRY", "PUNJAB",
                    "RAJASTHAN", "TAMIL NADU", "TELANGANA", "THE DADRA AND NAGAR HAVELI AND DAMAN AND DIU", "UTTAR PRADESH", "WEST BENGAL"]

detail = {}
irrad = {}

for state in states_list1:
    detail[state] = list1

for state in states_list2:
    detail[state] = list2

irrad = {"ARUNACHAL PRADESH": 1046.26, "ASSAM": 1046.26, "HIMACHAL PRADESH": 1046.26, "JAMMU and KASHMIR": 1046.26,
             "MANIPUR": 1046.26, "MEGHALAYA": 1046.26, "MIZORAM": 1046.26, "NAGALAND": 1046.26, "SIKKIM": 1046.26,
             "TRIPURA": 1046.26, "UTTARAKHAND": 1046.26, "ANDAMAN and NICOBAR ISLANDS": 1156.39, "BIHAR": 1156.39,
             "CHANDIGARH": 1156.39, "HARYANA": 1156.39, "JHARKHAND": 1156.39, "NCT OF DELHI": 1156.39, "ORISSA": 1156.39,
             "PUNJAB": 1156.39, "UTTAR PRADESH": 1156.39, "WEST BENGAL": 1156.39, "ANDHRA PRADESH": 1266.52, "CHHATISGARH": 1266.52,
             "GOA": 1266.52, "GUJARAT": 1266.52, "KARNATAKA": 1266.52, "KERALA": 1266.52, "LADAKH": 1266.52,
             "LAKSHADWEEP": 1266.52, "MADHYA PRADESH": 1266.52, "MAHARASHTRA": 1266.52, "PUDUCHERRY": 1266.52,
             "RAJASTHAN": 1266.52, "TAMIL NADU": 1266.52, "TELANGANA": 1266.52,
             "THE DADRA AND NAGAR HAVELI AND DAMAN AND DIU": 1266.52}





def calc_from_area(state, area, category, rate):
    capacity = area * irrad[state] /10000
    cap = int(capacity) 
    cap= cap-(cap % 5)
    return calc_from_capacity(state, cap, category, rate)


def calc_from_budget(state, budget, category, rate):
    temp = detail[state]
    cap = 0
    cost = 0
    if budget < temp[0]:
        cap = 0
    else:
        i = 1
        while cost <= budget:
            if i <= 1:
                cost = temp[0] * i
            elif 1 < i <= 2:
                cost = temp[1] * i
            elif 2 < i <= 3:
                cost = temp[2] * i
            elif 3 < i <= 10:
                cost = temp[3] * i
            elif 10 < i <= 100:
                cost = temp[4] * i
            else:
                cost = temp[5] * i
            cap = i
            i += 1
    return calc_from_capacity(state, cap, category, rate)


def calc_from_capacity(state, capacity, category, rate):
    ans = []
    cap = capacity
    prod = 0.0
    ans.append(irrad[state])
    if irrad[state] == 1046.26:
        prod = 4.1
    elif irrad[state]== 1156.39:
        prod = 4.6
    else:
        prod = 5.0
    ans.append(prod)
    ans.append(float(cap))
    cost = 0
    temp = detail[state]
    if cap <= 1:
        ans.append(float(temp[0]))
        cost = temp[0] * cap
    elif 1 < cap <= 2:
        ans.append(float(temp[1]))
        cost = temp[1] * cap
    elif 2 < cap <= 3:
        ans.append(float(temp[2]))
        cost = temp[2] * cap
    elif 3 < cap <= 10:
        ans.append(float(temp[3]))
        cost = temp[3] * cap
    elif 10 < cap <= 100:
        ans.append(float(temp[4]))
        cost = temp[4] * cap
    else:
        ans.append(float(temp[5]))
        cost = temp[5] * cap
    ans.append(float(cost))
    subsidy = 0
    if category == "Residential (Private)":  # Send Residential(Private)
        if cap <= 3:
            subsidy = temp[6] * cap
        elif 3 < cap <= 10:
            subsidy = temp[6] * 3 + (temp[7] * (cap - 3))
        else:
            subsidy = temp[8]

    if category == "Residential (Society)" :
        subsidy = 7294 * cap
    
    net_cost = round(cost - subsidy, 2)
    ans.append(net_cost)
    annual_elec = int(cap * prod * 300)
    ans.append(annual_elec)
    total_elec = int(annual_elec * 25)
    ans.append(total_elec)

    month_save = round((annual_elec / 12) * rate,2)
    annual_save = round(annual_elec * rate,2)
    overall_save = round(annual_save * 25,2)
    ans.append(month_save)
    ans.append(annual_save)
    ans.append(overall_save)

    break_even = round(net_cost / annual_save,2)
    ans.append(break_even)
    return ans



print(calc_from_area("HARYANA", 45, "Private", 10))
