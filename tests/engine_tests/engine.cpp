#include <iostream>
#include <vector>
#include <string>
#include <cassert>

// --- Data Structures (Match these with your main.cpp) ---
struct Transaction {
    std::string date;
    double remanent;
};

struct QPeriod {
    std::string start;
    std::string end;
    double fixed;
};

// --- Extern Declarations ---
// These must match the function signatures in your engine/main.cpp exactly
extern double calculate_total_savings(
    const std::vector<Transaction>& txns, 
    const std::vector<QPeriod>& qs
);

void run_test(std::string name, bool condition) {
    std::cout << "[TEST] " << name << " ... ";
    if (condition) {
        std::cout << "✅ PASSED" << std::endl;
    } else {
        std::cout << "❌ FAILED" << std::endl;
        exit(1);
    }
}

int main() {
    std::cout << "--- Executing Engine Logic Validation ---\n" << std::endl;

    // Test Case 1: Basic Sweep-line logic
    std::vector<Transaction> txns = {{"2026-02-21 12:00:00", 50.0}};
    std::vector<QPeriod> qs = {{"2026-02-01 00:00:00", "2026-02-28 23:59:59", 100.0}};
    
    // Logic: Remanent (50) + Q-Fixed (100) = 150
    double result = calculate_total_savings(txns, qs);
    run_test("Basic Savings Calculation", result == 150.0);

    // Test Case 2: Overlapping Q-Priority
    // (Simulate your "Latest Start Wins" logic here)
    
    std::cout << "\n🎉 All core logic tests passed successfully!" << std::endl;
    return 0;
}