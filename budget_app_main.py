from bud_app_class import BudApp

# App's dashboard
def Dashboard():
    print('\nDashboard')
    print('-'*9)
    print(' 1. New Transaction')
    print(' 2. Show Balance left')
    print(' 3. Show Amount Spent')
    print(' 4. Show Initial Budget')
    print(' 5. Exit App')
    print('Enter your choice: ', end='')
    valid_input = False
    while not valid_input:
        usr_choice = input()

        if usr_choice in ['1','2','3','4','5']:
            valid_input = True
            return int(usr_choice)
        else:
            print('Incorrect Choice.  Enter again:', end=' ')


# The Main function
def starting_main():
    greeting = 'Welcome to Green Goblin!'
    tagline = 'An app for all your budgeting needs'
    bud = BudApp(0.0, 0.0, 0.0, 0.0)
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
                bud.balance = usr_bal
        
        except(ValueError):
            print("The value you entered is invalid. Please try again.\n")

    #Transitions to Dashboard
    quit_program = False
    while not quit_program:
        usr_choice = Dashboard()

        match usr_choice:
            case 1:
                bud.Transaction()
            case 2:
                bud.Balance_left()
            case 3:
                bud.Spent()
            case 4:
                bud.Init_Bal()
            case 5:
                quit_program = True
                print('\nGoodbye!')
                exit()
            case _:
                print('\nInput was invalid. Please try again.')


if __name__ == "__main__":
    starting_main()