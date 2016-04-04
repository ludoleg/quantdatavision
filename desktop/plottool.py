import matplotlib.pyplot as plt

def overplotgraph(angle,diff,BGpoly,Sum, graphlist,filename):
    fig = plt.figure(figsize=(15,5)) 
    plt.plot(angle, diff, linestyle="none",  marker=".",  color="black")
    fig.patch.set_facecolor('white')
    plt.xlabel('2-theta (deg)')
    plt.ylabel('intensity')
    #plt.plot(BGX, BGY, linestyle="none",  marker="o", color="yellow")  #plots data og calculate linear background
    #plt.plot(angle, Diffmodel, linestyle="solid", color="green")
    plt.plot(angle, BGpoly, linestyle="solid", color="red")
    plt.plot(angle, Sum, linestyle="solid", color="green")
    plt.xlim(5,55)
    plt.ylim(0,max(diff)*2)

    offset = max(diff)/2*3
    difference_magnification = 1
    difference = (diff - Sum) * difference_magnification
    offsetline = [offset]*len(angle)
    plt.plot(angle, difference+offset, linestyle="solid", color="red")
    plt.plot(angle, offsetline, linestyle="solid", color="pink")
    
    FOM = sum(abs(diff-Sum))/len(diff)
    plt.text(6, offset/10*12, filename, fontsize=12, color="black")
    #plt.text(6, offset/10*11, "Calculated with PatDB", fontsize=12, color="black")
    plt.text(50, offset/10*12, "FOM = %.2f" %(FOM), fontsize=12, color="red")
    vertpos = offset/10*9
    for i in range(0,len(graphlist)):
        minname = graphlist[i][0]
        if len(minname)>12:
            minname = '%s.' %minname[0:12]
        plt.text(6, vertpos,"%s :" %minname, fontsize=12, color="blue")
        plt.text(12, vertpos,"%.1f" %float(graphlist[i][1]), fontsize=12, color="blue")
        vertpos -= offset/15
    if len(graphlist) == 10:
        plt.text(6, vertpos,"...", fontsize=12, color="blue")

    plt.show()

    return
