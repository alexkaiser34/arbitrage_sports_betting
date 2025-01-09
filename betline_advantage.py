import sys

print("WELCOME TO BETLINE ADVANTAGE CALCULATOR\n\n")

if len(sys.argv) > 1 and sys.argv[1] == "--help":
    print("This tool will tell you if you can make certain money with alternate lines")
    print("\nFor example, say a player has the following alternate and standard line:")
    print("\t4+ assist @ +160")
    print("\tO/U 3.5 assists @ -120")
    print("\nThe difference in odds means you can take U 3.5 and the 4+ assist alternate line to make")
    print("guaranteed money ($500 bet guarantees $37 dollar profit in this case)!")
    print("\nThis tool will tell you how much to spend on each line to make the maximum GUARANTEED profit")
    exit(0)

total_wager = int(input("Please enter the total amount of money you are willing to wager: "))
over_odds = int(input("Please enter the american odds for the over: "))
under_odds = int(input("Please enter the american odds for the under: "))
print("\nCalculating....\n")

over_decimal = 0
under_decimal = 0

if over_odds > 0:
    over_decimal = (over_odds/100)+1
else:
    over_decimal = (100/abs(over_odds))+1
    
if under_odds > 0:
    under_decimal = (under_odds/100)+1
else:
    under_decimal = (100/abs(under_odds))+1
    
    
max_amount = 0
over_max = 0
under_max = 0
prev_max = 0

win_under = 0
win_over = 0
win_profit = 0

for i in range(1,total_wager):
    over_spend = i
    under_spend = total_wager - i
    iteration_profit = 0
    
    over_gain = (over_spend * over_decimal) - total_wager
    under_gain = (under_spend * under_decimal) - total_wager
    
    if (over_gain > 0) and (under_gain > 0):
        iteration_profit = min(over_gain, under_gain)
        
    if iteration_profit > 0:
        max_amount = max(iteration_profit, max_amount)
        if max_amount != prev_max:
            win_over = over_spend
            win_under = under_spend
            win_profit = max_amount
        
    prev_max = max_amount
        
#     for j in range(1, total_wager):
#         under_spend = j
        
        
        
#         profit = 0
        
#         if over_gain > under_gain:
#             profit = over_gain - under_gain
#         else:
#             profit = under_gain - over_gain
        
#         # max_amount = max(over_gain, max_amount)
#         max_amount = max(profit, max_amount)
        
#         if (max_amount != prev_max):
#             win_over = over_spend
#             win_under = under_spend
#             win_profit = max_amount
        
#         prev_max = max_amount

if max_amount <= 0:
    print("no money can be won")
else:
    print("\nGUARENTEED MONEY CAN BE MADE\n")
    print("Under bet: " + str(win_under) + " @ " + str(under_odds))
    print("\nOver bet: " + str(win_over) + " @ " + str(over_odds))
    print("\n" + str(total_wager) + " bet pays total of " + str(round(max_amount + total_wager, 2)) + " for profit of " + str(round(max_amount, 2)))

