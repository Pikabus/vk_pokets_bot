def even_fibb_elems(n):
    i = 0
    previos_elem, elem = 1, 0
    while i < n:
        if elem % 2 == 0:
            i += 1
            print(elem)
        previos_elem, elem = elem, previos_elem + elem


n = 4
even_fibb_elems(n)
