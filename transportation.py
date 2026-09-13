import numpy as np

def get_penalties(costs, active_rows, active_cols):
    row_penalties = []
    for r in active_rows:
        temp_costs = []
        for c in active_cols:
            temp_costs.append(costs[r][c])
        temp_costs.sort()
        
        if len(temp_costs) > 1:
            pen = temp_costs[1] - temp_costs[0]
        else:
            pen = temp_costs[0]
        row_penalties.append((pen, r))
        
    col_penalties = []
    for c in active_cols:
        temp_costs = []
        for r in active_rows:
            temp_costs.append(costs[r][c])
        temp_costs.sort()
        
        if len(temp_costs) > 1:
            pen = temp_costs[1] - temp_costs[0]
        else:
            pen = temp_costs[0]
        col_penalties.append((pen, c))
        
    return row_penalties, col_penalties

def vam(supply, demand, costs):
    supp = supply.copy()
    dem = demand.copy()
    rows = len(supp)
    cols = len(dem)
    ans = np.zeros((rows, cols))
    
    active_rows = []
    for i in range(rows):
        active_rows.append(i)
        
    active_cols = []
    for j in range(cols):
        active_cols.append(j)
    
    while len(active_rows) > 0 and len(active_cols) > 0:
        row_pen, col_pen = get_penalties(costs, active_rows, active_cols)
        
        max_r_pen = -1
        max_r_idx = -1
        for p, r in row_pen:
            if p > max_r_pen:
                max_r_pen = p
                max_r_idx = r
                
        max_c_pen = -1
        max_c_idx = -1
        for p, c in col_pen:
            if p > max_c_pen:
                max_c_pen = p
                max_c_idx = c
        
        if max_r_pen >= max_c_pen:
            r = max_r_idx
            min_cost = 999999
            c = -1
            for col in active_cols:
                if costs[r][col] < min_cost:
                    min_cost = costs[r][col]
                    c = col
        else:
            c = max_c_idx
            min_cost = 999999
            r = -1
            for row in active_rows:
                if costs[row][c] < min_cost:
                    min_cost = costs[row][c]
                    r = row
            
        allocate_val = min(supp[r], dem[c])
        ans[r][c] = allocate_val
        supp[r] -= allocate_val
        dem[c] -= allocate_val
        
        if supp[r] == 0 and r in active_rows:
            active_rows.remove(r)
        elif dem[c] == 0 and c in active_cols:
            active_cols.remove(c)
            
    return ans

def find_loop(start_node, basic_cells):
    def dfs(curr, visited, is_horiz):
        if curr == start_node and len(visited) > 3:
            return visited
            
        r = curr[0]
        c = curr[1]
        
        for next_node in basic_cells:
            next_r = next_node[0]
            next_c = next_node[1]
            
            if next_node not in visited or (next_node == start_node and len(visited) > 3):
                if is_horiz and next_r == r and next_c != c:
                    res = dfs(next_node, visited + [next_node], False)
                    if res != None: return res
                elif not is_horiz and next_c == c and next_r != r:
                    res = dfs(next_node, visited + [next_node], True)
                    if res != None: return res
        return None

    loop = dfs(start_node, [start_node], True)
    if loop == None:
        loop = dfs(start_node, [start_node], False)
    return loop

def modi(costs, allocations):
    rows = len(costs)
    cols = len(costs[0])
    
    while True:
        basic_cells = []
        for i in range(rows):
            for j in range(cols):
                if allocations[i][j] > 0:
                    basic_cells.append((i, j))
        
        req_alloc = rows + cols - 1
        if len(basic_cells) < req_alloc:
            print("\nDegeneracy detected! Need", req_alloc, "allocations but got", len(basic_cells))
            print("Returning VAM solution instead.")
            return allocations

        u = [None] * rows
        v = [None] * cols
        u[0] = 0 
        
        while (None in u) or (None in v):
            for cell in basic_cells:
                r = cell[0]
                c = cell[1]
                if u[r] is not None and v[c] is None:
                    v[c] = costs[r][c] - u[r]
                elif v[c] is not None and u[r] is None:
                    u[r] = costs[r][c] - v[c]
                    
        optimal = True
        min_delta = 0
        entering_cell = None
        
        for r in range(rows):
            for c in range(cols):
                if allocations[r][c] == 0:
                    delta = costs[r][c] - u[r] - v[c]
                    if delta < min_delta:
                        min_delta = delta
                        entering_cell = (r, c)
                        optimal = False
                        
        if optimal == True:
            break 
            
        basic_cells.append(entering_cell)
        loop = find_loop(entering_cell, basic_cells)
        
        minus_cells = []
        for i in range(1, len(loop), 2):
            minus_cells.append(loop[i])
            
        shift_val = 999999
        for cell in minus_cells:
            if allocations[cell[0]][cell[1]] < shift_val:
                shift_val = allocations[cell[0]][cell[1]]
        
        for i in range(len(loop) - 1): 
            r = loop[i][0]
            c = loop[i][1]
            if i % 2 == 0:
                allocations[r][c] += shift_val 
            else:
                allocations[r][c] -= shift_val 

    return allocations

if __name__ == "__main__":
    print("--- Transportation Problem Solver ---")
    num_sources = int(input("Enter number of sources: "))
    num_dests = int(input("Enter number of destinations: "))
    
    print("\nEnter supply array:")
    supply = list(map(float, input().strip().split()))
    
    print("\nEnter demand array:")
    demand = list(map(float, input().strip().split()))
    
    print(f"\nEnter {num_sources}x{num_dests} cost matrix row by row:")
    costs = []
    for i in range(num_sources):
        row = list(map(float, input().strip().split()))
        costs.append(row)
        
    costs = np.array(costs)
    
    sum_supp = 0
    for s in supply:
        sum_supp += s
        
    sum_dem = 0
    for d in demand:
        sum_dem += d
        
    if sum_supp != sum_dem:
        print("\nError: Unbalanced problem!")
    else:
        print("\nRunning VAM...")
        initial_ans = vam(supply.copy(), demand.copy(), costs)
        print("Initial Allocation Matrix:")
        print(initial_ans)
        
        init_cost = 0
        for i in range(num_sources):
            for j in range(num_dests):
                init_cost += initial_ans[i][j] * costs[i][j]
        print(f"Initial Cost = {init_cost}")
        
        print("\nRunning MODI...")
        final_ans = modi(costs, initial_ans)
        print("Final Optimal Matrix:")
        print(final_ans)
        
        final_cost = 0
        for i in range(num_sources):
            for j in range(num_dests):
                final_cost += final_ans[i][j] * costs[i][j]
        print(f"Minimum Cost = {final_cost}")