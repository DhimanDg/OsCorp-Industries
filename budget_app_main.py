from bud_class import BudApp

# Dashboard Prototype (will delete later)
def Dashboard():
    print('\nDashboard')
    print('-'*9)
    print(' 1. New Transaction')
    print(' 2. Show Balance left')
    print(' 3. Show Amount Spent')
    print(' 4. Show Past Transactions')
    print(' 5. Remove Transaction')
    print(' 6. Show Initial Budget')
    print(' 7. Add New Budget (Unfinished)')
    print(' 8. Remove Budget (Unfinished)')
    print(' 9. Switch Budget (Unfinished)')
    print(' 10. Change Current Budget')
    print(' 11. Set Spending Limit for Category')
    print(' 12. Remove Spending Limit')
    print(' 13. Set Budget Limit')
    print(' 14. Remove Budget Limit')
    print(' 15. Exit App')
    print('Enter your choice: ', end='')
    valid_input = False
    while not valid_input:
        usr_choice = input()

        if usr_choice in ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15']:
            valid_input = True
            return int(usr_choice)
        else:
            print('Incorrect Choice.  Enter again:', end=' ')


# The Main function
def main():
    greeting = 'Welcome to Green Goblin!'
    tagline = 'An app for all your budgeting needs'
    bud = BudApp(0.0, 0.0) #Sets variables in BudApp as floats
    
    print(f"{greeting:^35}")
    print(f"{tagline}")
    print('*'*35)
    valid_input = False

    #Set the user's initial budget
    while not valid_input:
        try:
            print("Enter your budget: ", end="$")
            usr_bal = float(input())

            if usr_bal <= 0:
                print("Invalid budget value. Please try again.\n")
            elif usr_bal > 0:
                valid_input = True
                bud.iniBud = usr_bal
                bud.balance += usr_bal
        
        except(ValueError):
            print("The value you entered is invalid. Please try again.\n")

    #Transitions to Dashboard
    quit_program = False
    while not quit_program:
        usr_choice = Dashboard()

        match usr_choice:
            case 1:
                bud.Transaction(None)
            case 2:
                bud.Balance_left()
            case 3:
                bud.Spent()
            case 4:
                bud.Past_Tra()
            case 5:
                bud.Remove_tra()
            case 6:
                bud.Init_Bud()
            case 7:
                pass
            case 8:
                pass
            case 9:
                pass
            case 10:
                bud.Change_Bud()
            case 11:
                bud.Cat_Limit()
            case 12:
                bud.RemoveCatLim()
            case 13:
                bud.Bud_Limit()
            case 14:
                bud.RemoveBudLim()
            case 15:
                quit_program = True
                print('\nGoodbye!')
                exit()
            case _:
                print('\nInput was invalid. Please try again.')

if __name__ == "__main__":
    main()