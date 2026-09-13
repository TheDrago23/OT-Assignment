def solve_big_m(tableau, basic_vars, num_vars, num_cons):
    while True:
        z_row = tableau[num_cons]
        
        is_optimal = True
        for j in range(num_vars):
            if z_row[j] > 0.0000001:
                is_optimal = False
                break
                
        if is_optimal == True:
            break
            
        entering_col = 0
        max_val = z_row[0]
        for j in range(1, num_vars):
            if z_row[j] > max_val:
                max_val = z_row[j]
                entering_col = j
                
        leaving_row = -1
        min_ratio = 999999999
        
        for i in range(num_cons):
            if tableau[i][entering_col] > 0:
                ratio = tableau[i][-1] / tableau[i][entering_col]
                if ratio < min_ratio:
                    min_ratio = ratio
                    leaving_row = i
                    
        if leaving_row == -1:
            print("Error: Unbounded problem")
            return None, None
            
        pivot = tableau[leaving_row][entering_col]
        for j in range(num_vars + 1):
            tableau[leaving_row][j] = tableau[leaving_row][j] / pivot
            
        for i in range(num_cons + 1):
            if i != leaving_row:
                factor = tableau[i][entering_col]
                for j in range(num_vars + 1):
                    tableau[i][j] = tableau[i][j] - (factor * tableau[leaving_row][j])
                    
        basic_vars[leaving_row] = entering_col

    ans = [0] * num_vars
    for i in range(num_cons):
        idx = basic_vars[i]
        if idx < num_vars:
            ans[idx] = tableau[i][-1]
            
    z_val = tableau[num_cons][-1]
    return ans, z_val

if __name__ == "__main__":
    print("--- Big-M Simplex Solver ---")
    num_vars = int(input("Enter number of variables: "))
    num_cons = int(input("Enter number of constraints: "))
    
    print("\nEnter initial tableau row by row:")
    tableau = []
    for i in range(num_cons + 1):
        row = list(map(float, input().strip().split()))
        tableau.append(row)
        
    print("\nEnter initial basic variable indices:")
    basic_vars = list(map(int, input().strip().split()))
    
    sol, z_val = solve_big_m(tableau, basic_vars, num_vars, num_cons)
    
    if sol != None:
        print("\nFinal Solution:")
        for i in range(num_vars):
            print(f"x{i+1} = {sol[i]}")
        print(f"Objective Value = {-z_val}")