from typing import List

# TODO: Use get_possible_values to update self.domain


class Board:
    def __init__(self, N: int,  clues: List[List[int]]):
        self.N = N

        # - Create N x N grid filled with 0s
        self.grid = [[0 for _ in range(N)] for _ in range(N)]

        # - Store clues for all 4 sides
        self.top_clues = clues[0]
        self.right_clues = clues[1]
        self.bottom_clues = clues[2]
        self.left_clues = clues[3]

        # - Initialize domain for each cell (1 to N)
        self.domain = [[[x for x in range(1, N+1)]
                        for _ in range(N)] for _ in range(N)]

        self.init_constraints = False
        pass

    def is_valid(self) -> bool:
        # Check if current grid state is valid
        # - Check rows and columns for duplicates
        column_sets = [set() for _ in range(self.N)]
        row_sets = [set() for _ in range(self.N)]
        invalid = False

        for i in range(self.N):
            for j in range(self.N):
                if self.grid[i][j] not in row_sets[i] and self.grid[i][j] not in column_sets[j]:
                    row_sets[i].add(self.grid[i][j])
                    column_sets[j].add(self.grid[i][j])
                else:
                    invalid = True
                    break

            if invalid is not True:
                break

        # - Check if the grid is valid. Some grid cell might still have value 0 but the clue pairs should not be exceeded.
        if invalid is False:

            transposed_grid = self.transpose_matrix(self.N, self.grid)

            # Row checks
            for i in range(self.N):
                if self.check_visibility(left_clue=self.left_clues[i], right_clue=self.right_clues[i], buildings=self.grid[i]) != 1 and invalid is not True:
                    invalid = True

            # Column checks
            for i in range(self.N):
                if self.check_visibility(left_clue=self.top_clues[i], right_clue=self.bottom_clues[i], buildings=transposed_grid[i]) != 1 and invalid is not True:
                    invalid = True

    def get_possible_values(self, row: int, col: int) -> List[int]:
        # Return available values for given cell
        possible_values = set(range(1, self.N + 1))
        for i in range(self.N):
            if self.grid[row][i] in possible_values:
                possible_values.remove(self.grid[row][i])

        for i in range(self.N):
            if self.grid[i][col] in possible_values:
                possible_values.remove(self.grid[row][i])

        # - Return current domain for the specified cell
        return list(possible_values)

    def apply_constraint(self) -> bool:
        if not self.init_constraints:
            self.init_constraints = True

            # Initial constraint propagation based on clues
            for i in range(self.N):
                # Apply constraints based on the top and bottom clues
                if self.top_clues[i] == 1:
                    self.domain[0][i] = [self.N]
                elif self.top_clues[i] == self.N:
                    for j in range(self.N):
                        self.domain[j][i] = list(range(1, self.N + 1 - j))

                if self.bottom_clues[i] == 1:
                    self.domain[self.N - 1][i] = [self.N]
                elif self.bottom_clues[i] == self.N:
                    for j in range(self.N):
                        self.domain[self.N - 1 -
                                    j][i] = list(range(j + 1, self.N + 1))

                # Apply constraints based on the left and right clues
                if self.left_clues[i] == 1:
                    self.domain[i][self.N - 1] = [self.N]
                elif self.left_clues[i] == self.N:
                    for j in range(self.N):
                        self.domain[i][self.N - 1 -
                                       j] = list(range(j + 1, self.N + 1))

                if self.right_clues[i] == 1:
                    self.domain[i][0] = [self.N]
                elif self.right_clues[i] == self.N:
                    for j in range(self.N):
                        self.domain[i][j] = list(range(1, self.N + 1 - j))

        # Base case to detect contradictions if any cell has an empty domain
        for row in range(self.N):
            for col in range(self.N):
                if len(self.domain[row][col]) == 0:
                    return False  # Domain empty = contradiction

        # Update cell domains based on current grid state
        for row in range(self.N):
            for col in range(self.N):
                if self.grid[row][col] != 0:  # Skip filled cells
                    continue

                # Get possible values for the current cell
                possible_values = self.get_possible_values(row, col)
                self.domain[row][col] = [
                    val for val in self.domain[row][col] if val in possible_values
                ]

                # Assign values to cells with singleton domains
                if len(self.domain[row][col]) == 1:
                    self.grid[row][col] = self.domain[row][col][0]

        # Dictionaries to track unique values in rows and columns
        row_dict = [{k: 0 for k in range(1, self.N + 1)}
                    for _ in range(self.N)]
        col_dict = [{k: 0 for k in range(1, self.N + 1)}
                    for _ in range(self.N)]
        changed = False

        # Count occurrences of possible values in row_dict and col_dict
        for row in range(self.N):
            for col in range(self.N):
                if self.grid[row][col] == 0:  # Only check cells that are not filled
                    for value in self.domain[row][col]:
                        row_dict[row][value] += 1
                        col_dict[col][value] += 1

        # Filter row_dict and col_dict to keep only values that are unique in each row/column
        for i in range(self.N):
            row_dict[i] = {k: v for k, v in row_dict[i].items() if v == 1}
            col_dict[i] = {k: v for k, v in col_dict[i].items() if v == 1}

        # Assign unique values in cells based on row_dict and col_dict
        for row in range(self.N):
            for col in range(self.N):
                if self.grid[row][col] != 0:
                    continue  # Skip filled cells

                for value in self.domain[row][col]:
                    if value in row_dict[row] or value in col_dict[col]:
                        # Unique value found, assign to grid
                        self.grid[row][col] = value
                        # Update domain to reflect the assigned value
                        self.domain[row][col] = [value]
                        changed = True
                        break  # Move to the next cell after assignment

        # Recursively reapply constraints if changes were made
        if changed:
            return self.apply_constraint()

        return True  # Return True if no changes were made, indicating stability

    def check_visibility(self, left_clue: int, right_clue: int, buildings: List[int]) -> bool:
        # TODO: Verify if building arrangement satisfies clue pair
        # - Count visible buildings from left
        # - Count visible buildings from right
        # - Compare with clues
        # - return 0 if the visibility is exactly as clue
        # - return 1 if the visibility is more than clues
        # - return -1 if the visibility is less than clues
        pass

    def search(self) -> bool:
        # TODO: Implement backtracking search
        # 1. Find cell with smallest domain
        # 2. For each possible value:
        #    - Assign value
        #    - Apply constraints
        #    - Recursively search
        #    - If solution found, return True
        #    - If dead end, backtrack
        # 3. Return False if no solution found
        pass

    def transpose_matrix(N: int, matrix: list[list[int]]) -> list[list[int]]:
        # Create an empty matrix to store the transposed matrix
        transposed = [[0] * N for _ in range(N)]

        # Perform the transpose operation
        for i in range(N):
            for j in range(N):
                transposed[j][i] = matrix[i][j]

        return transposed


def solve_skyscraper(clues: List[List[int]]) -> List[List[int]]:
    # TODO: Main solver function
    # 1. Create board instance
    # 2. Handle initial constraints (1,N clues)
    # 3. Apply constraint propagation
    # 4. If not solved, start backtracking search
    # 5. Return solution grid or None if no solution
    pass
