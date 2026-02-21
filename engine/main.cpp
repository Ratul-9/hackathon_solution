#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <set>
#include <cmath>
#include <iomanip>
#include "nlohmann/json.hpp" // Required for JSON parsing
#include <chrono>

// USE ORDERED JSON TO PRESERVE EXACT KEY SEQUENCE
using json = nlohmann::ordered_json;
using namespace std;

// Quick string to integer epoch conversion
long long parse_date(const string& s) {
    long long res = 0;
    for (char c : s) {
        if (isdigit(c)) res = res * 10 + (c - '0');
    }
    return res;
}

struct Event {
    long long time;
    int type; 
    int id;
    long long val;
    long long q_start;

    bool operator<(const Event& other) const {
        if (time != other.time) return time < other.time;
        return type < other.type; 
    }
};

struct Transaction {
    long long time;
    long long amount;
    long long ceiling;
    long long final_remanent;
    int original_id;
};

vector<long long> q_fixed_amounts;

// --- TAX & FINANCIAL LOGIC ---
double calculate_tax(double income) {
    double tax = 0;
    if (income > 1500000) { tax += (income - 1500000) * 0.30; income = 1500000; }
    if (income > 1200000) { tax += (income - 1200000) * 0.20; income = 1200000; }
    if (income > 1000000) { tax += (income - 1000000) * 0.15; income = 1000000; }
    if (income > 700000)  { tax += (income - 700000) * 0.10; }
    return tax;
}

pair<double, double> calculate_nps_metrics(long long invested, double yearly_wage, int age, double inflation) {
    double max_deduction = min({(double)invested, yearly_wage * 0.10, 200000.0});
    
    double tax_without = calculate_tax(yearly_wage);
    double tax_with = calculate_tax(yearly_wage - max_deduction);
    double rebate = tax_without - tax_with;

    int t = (age < 60) ? (60 - age) : 5;
    double r = 0.0711; 
    double A = invested * pow(1 + r, t);
    double real_val = A / pow(1 + inflation, t);
    
    return {real_val, rebate}; 
}

double calculate_index_metrics(long long invested, int age, double inflation) {
    int t = (age < 60) ? (60 - age) : 5;
    double r = 0.1449; 
    double A = invested * pow(1 + r, t);
    return A / pow(1 + inflation, t);
}

int main() {
    auto start_perf = chrono::high_resolution_clock::now();
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    json input_data;
    if (!(cin >> input_data)) return 0;

    string mode = input_data.value("mode", "nps");
    int age = input_data["age"];
    double monthly_wage = input_data["wage"];
    
    // BUG FIX 1: Convert percentage to decimal
    double inflation = (double)input_data["inflation"] / 100.0;
    
    // BUG FIX 2: Convert monthly wage to yearly for tax calculation
    double yearly_wage = monthly_wage * 12.0;

    vector<Transaction> txns; 
    vector<Event> events;

    double global_total_amount = 0;
    double global_total_ceiling = 0;

    int txn_idx = 0;
    for (const auto& item : input_data["transactions"]) {
        long long t_time = parse_date(item["date"]);
        double amt = item["amount"];
        
        long long ceiling = (long long)(ceil(amt / 100.0) * 100);
        
        global_total_amount += amt;
        global_total_ceiling += ceiling;

        txns.push_back({t_time, (long long)amt, ceiling, 0, txn_idx});
        events.push_back({t_time, 3, txn_idx, 0, 0});
        txn_idx++;
    }

    int q_idx = 0;
    for (const auto& q : input_data["q_periods"]) {
        events.push_back({parse_date(q["start"]), 2, q_idx, 0, parse_date(q["start"])});
        events.push_back({parse_date(q["end"]), 4, q_idx, 0, parse_date(q["start"])});
        q_fixed_amounts.push_back(q["fixed"]);
        q_idx++;
    }

    int p_idx = 0;
    for (const auto& p : input_data["p_periods"]) {
        events.push_back({parse_date(p["start"]), 1, p_idx, (long long)p["extra"], 0});
        events.push_back({parse_date(p["end"]), 5, p_idx, (long long)p["extra"], 0});
        p_idx++;
    }

    sort(events.begin(), events.end());
    long long current_p_sum = 0;
    set<pair<long long, int>> active_q; 

    for (const auto& ev : events) {
        if (ev.type == 1) current_p_sum += ev.val;
        else if (ev.type == 2) active_q.insert({-ev.q_start, ev.id});
        else if (ev.type == 4) active_q.erase({-ev.q_start, ev.id});
        else if (ev.type == 5) current_p_sum -= ev.val;
        else if (ev.type == 3) { 
            long long amt = txns[ev.id].amount;
            long long remanent = (amt % 100 == 0) ? 0 : 100 - (amt % 100);

            if (!active_q.empty()) {
                remanent = q_fixed_amounts[active_q.begin()->second];
            }
            remanent += current_p_sum;
            txns[ev.id].final_remanent = remanent;
        } 
    }

    sort(txns.begin(), txns.end(), [](const Transaction& a, const Transaction& b) {
        return a.time < b.time;
    });

    vector<long long> txn_times(txns.size());
    vector<long long> pref_sums(txns.size() + 1, 0);

    for (size_t i = 0; i < txns.size(); ++i) {
        txn_times[i] = txns[i].time;
        pref_sums[i + 1] = pref_sums[i] + txns[i].final_remanent;
    }


    auto end_perf = chrono::high_resolution_clock::now();
    auto duration = chrono::duration_cast<chrono::microseconds>(end_perf - start_perf);

    json response;
    // Exactly matches the image order
    response["totalTransactionAmount"] = round(global_total_amount * 10.0) / 10.0;
    response["totalCeiling"] = round(global_total_ceiling * 10.0) / 10.0;
    response["savingsByDates"] = json::array();

    for (const auto& k : input_data["k_periods"]) {
        long long k_start = parse_date(k["start"]);
        long long k_end = parse_date(k["end"]);

        auto it_start = lower_bound(txn_times.begin(), txn_times.end(), k_start);
        auto it_end = upper_bound(txn_times.begin(), txn_times.end(), k_end);

        long long invested = 0;
        if (it_start < it_end) {
            invested = pref_sums[distance(txn_times.begin(), it_end)] - pref_sums[distance(txn_times.begin(), it_start)];
        }

        double profit = 0, tax_benefit = 0;

        if (mode == "nps") {
            pair<double, double> res = calculate_nps_metrics(invested, yearly_wage, age, inflation);
            profit = res.first - invested;
            tax_benefit = res.second;
        } else {
            profit = calculate_index_metrics(invested, age, inflation) - invested;
        }

        json k_res;
        k_res["start"] = k["start"];
        k_res["end"] = k["end"];
        k_res["amount"] = round(invested * 10.0) / 10.0;
        k_res["profit"] = round(profit * 100.0) / 100.0;
        k_res["taxBenefit"] = round(tax_benefit * 10.0) / 10.0;
        
        response["savingsByDates"].push_back(k_res);
    }
    response["performance"] = {
        {"executionTimeUs", duration.count()},
        {"complexity", "O(N log N)"},
        {"engine", "C++20 Optimized"}
    };

    cout << response.dump(4) << endl;
    return 0;
}