from typing import List
# Ensure solve_skyscraper is adaptable for different N
from board import solve_skyscraper


def print_grid(grid: List[List[int]], top_clues: List[int], bottom_clues: List[int], left_clues: List[int], right_clues: List[int]) -> None:
    """Pretty print the skyscraper grid with clues."""
    N = len(grid)

    # Print top clues
    print("\n    ", end="")
    for clue in top_clues:
        print(f"{clue} ", end="")
    print("\n   ", "-" * (N * 2 + 1))

    # Print grid with left/right clues
    for i in range(N):
        print(f"{left_clues[i]}  |", end="")
        for j in range(N):
            print(f"{grid[i][j]} ", end="")
        print(f"| {right_clues[i]}")

    # Print bottom border and clues
    print("   ", "-" * (N * 2 + 1))
    print("    ", end="")
    for clue in bottom_clues:
        print(f"{clue} ", end="")
    print("\n")


def main():
    # Prompt user for grid size N
    N = int(input("Enter the size of the grid (N for an NxN puzzle): "))

    # Collecting clues
    print("Enter the top clues (space-separated):")
    top_clues = list(map(int, input().split()))

    print("Enter the right clues (space-separated):")
    right_clues = list(map(int, input().split()))

    print("Enter the bottom clues (space-separated):")
    bottom_clues = list(map(int, input().split()))

    print("Enter the left clues (space-separated):")
    left_clues = list(map(int, input().split()))

    # Ensure correct number of clues
    if not all(len(clues) == N for clues in [top_clues, right_clues, bottom_clues, left_clues]):
        print(f"Each clue list must contain exactly {N} clues.")
        return

    # Solve puzzle
    clues = [top_clues, right_clues, bottom_clues, left_clues]
    solution = solve_skyscraper(clues)

    if solution:
        print(f"\nSolution found for {N}x{N} puzzle!")
        print_grid(solution, top_clues, bottom_clues, left_clues, right_clues)
    else:
        print(f"\nNo solution exists for the given {N}x{N} clues.")


if __name__ == "__main__":
    main()
