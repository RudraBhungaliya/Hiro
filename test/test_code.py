t = int(input())
for _ in range(t):
    n = int(input())
    arr = list(map(int, input().split()))
    a = 1
    for i in range(1, n + 1):
        x = i
        while x % 2 == 0:
            x //= 2
        y = arr[i - 1]
        while y % 2 == 0:
            y //= 2
        if x != y:
            a = 0
    if a:
        print("YES")
    else:
        print("NO")
