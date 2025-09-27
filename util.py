def prob(shots, n):
    result = 0
    match n:
        case 0:
            sub = 1
            for s in shots:
                sub = sub * (1-s)
            result += sub
        case 1:
            for i in range(len(shots)):
                sub = 1
                for c in range(len(shots)):
                    if c == i:
                        sub = sub * shots[c]
                    else:
                        sub = sub * (1 - shots[c])
                result += sub
        case 2:
            if len(shots) < 2:
                return 0
            for i in range(len(shots)-1):
                for j in range(i+1,len(shots)):
                    sub = 1
                    for c in range(len(shots)):
                        if c == i or c == j:
                            sub = sub * shots[c]
                        else:
                            sub = sub * (1 - shots[c])
                    result += sub
        case 3:
            if len(shots) < 3:
                return 0
            for i in range(len(shots)-2):
                for j in range(i+1,len(shots)-1):
                    for k in range(j+1,len(shots)):
                        sub = 1
                        for c in range(len(shots)):
                            if c == i or c == j or c == k:
                                sub = sub * shots[c]
                            else:
                                sub = sub * (1 - shots[c])
                        result += sub
        case _:
            raise ValueError('3 is the largest number forget about it')
    return result