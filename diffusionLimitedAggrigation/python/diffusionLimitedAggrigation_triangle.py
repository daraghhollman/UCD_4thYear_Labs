import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import random
import sys

from tqdm import tqdm
from math import floor
from matplotlib.tri import Triangulation

from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable

rootPath = "/home/daraghhollman/Main/ucd_4thYearLabs/diffusionLimitedAggrigation/data/"
fileName = "continuedRun"

class Triangle:

    def __init__(self, vertices, index):
        self.vertices = [vertices[0], vertices[1], vertices[2]]
        self.neighbours = []
        self.index = index
        
    """
    def GetNeighbours(self, grid):
        myX, myY, myZ = (self.vertices[0], self.vertices[1], self.vertices[2])

        for triangle in grid:
            if triangle.vertices == [myX, myY, myZ]:
                continue

            elif triangle.vertices == [myX + 1, myY, myZ] or \
                    triangle.vertices == [myX - 1, myY, myZ]:
                print("YES")
    """
                


def main():

    sys.setrecursionlimit(10**6) # Increase recursion limit
    random.seed() # Uses system time as seed


    # Create Triangle Grid
    gridSize = 32
    gridCoordinates = [[row, col] for row in range(gridSize) for col in range(gridSize)]

    gridX = [el[0] for el in gridCoordinates]
    gridY = [el[1] for el in gridCoordinates]

    grid = Triangulation(gridX, gridY)
    triangleGrid = grid.triangles

    # Neighbors returns a list containing 3 indices of triangles
    neighbours = grid.neighbors

    triangles = [Triangle(el, i) for i, el in enumerate(triangleGrid)]

    for i, tri in enumerate(triangles):
        for neighbour in neighbours[i]:
            tri.neighbours.append(triangles[neighbour])

    

    plt.tripcolor(gridX, gridY, triangleGrid, [np.mean(el.vertices) for el in triangles])

    plt.show()
    
    return
    
    # note first argument is script path
    if len(sys.argv) == 4:
        command = str(sys.argv[1])
        number = int(sys.argv[2]) # represents grid size for command "start", or number of steps for command "continue"
        runPath = str(sys.argv[3])
    elif len(sys.argv) == 3:
        command = str(sys.argv[1])
        runPath = str(sys.argv[2])

    match command:
        case "start":
            NewRun(runPath, number)

        case "continue":
            ReloadRun(runPath, number)

        case "plot":
            ax = PlotRun(runPath)

            num = 15

            ax.xaxis.set_major_locator(ticker.MultipleLocator(num))
            ax.yaxis.set_major_locator(ticker.MultipleLocator(num))

            #ax.grid()

            plt.show()

# Notes
# Need to add parameter for diagnal attachment
# Notes from Meakin (3.4.3)
#   - Can reduce computational time by returning a particle to the launching circle whenever it leaves.





def PlotRun(filePath):
    loadGrid = np.load(filePath)

    rectLattice = Grid("Rectangular Lattice")

    rectLattice.grid = loadGrid

    ax = rectLattice.PlotGrid(figsize=(10,10), makeNan=True)

    return ax

def NewRun(filePath, gridSize):

    gridSizeX = gridSizeY = gridSize

    rectLattice = Grid("Rectangular Lattice")

    rectLattice.InstantiateGrid(gridSizeX, gridSizeY)

    # Create Origin
    rectLattice.FlipCell(floor(gridSizeX / 2), floor(gridSizeY / 2))

    for i in tqdm(range(10)):
        rectLattice.AgeCells()
        rectLattice.AddRandomCell()
        #rectLattice.PlotGrid(figsize=(10, 10))

    np.save(filePath, rectLattice.grid)

def ReloadRun(filePath, steps):

    rectLattice = Grid("Rectangular Lattice")

    loadGrid = np.load(filePath)

    rectLattice.grid = loadGrid

    for i in tqdm(range(steps)):
        rectLattice.AgeCells()
        rectLattice.AddRandomCell()
        #rectLattice.PlotGrid(figsize=(10, 10))

    np.save(filePath, rectLattice.grid)


class Grid:

    def __init__(self, name):
        self.name = name

    def InstantiateGrid(self, sizeX, sizeY):
        self.sizeX = sizeX
        self.sizeY = sizeY

        self.grid = np.zeros(shape=(self.sizeX, self.sizeY))

    def DisplayGrid(self):

        print("")
        print(self.name)
        print(self.grid)

    
    def PlotGrid(self, figsize, makeNan=False):

        # Change 0 cells to nan for plotting blank
        if makeNan:
            i = 0
            while i < len(self.grid):
                j = 0
                while j < len(self.grid[i]):

                    if self.grid[i][j] == 0:
                        self.grid[i][j] = np.nan

                    j += 1
                i += 1
        

        fig, ax = plt.subplots(1, 1, figsize=figsize)


        pcolor = ax.pcolormesh(self.grid, vmin=0)

        axDivider = make_axes_locatable(ax)
        cax = axDivider.append_axes("right", size="5%", pad="2%")
        plt.colorbar(pcolor, cax=cax, label="Cell Probabilitiy")

        return ax



    def GetCell(self, pointX, pointY):
        return self.grid[pointY][pointX]

    def SetCell(self, pointX, pointY, value):
        self.grid[pointY][pointX] = value

    def FlipCell(self, pointX, pointY):
        cellNumber = self.GetCell(pointX, pointY)

        if cellNumber >= 1:
            self.SetCell(pointX, pointY, 0)

        elif cellNumber == 0:
            self.SetCell(pointX, pointY, 1)

    def FindCellDistance(self, i, j, targetX, targetY):
        distanceX = abs(i - targetX)
        distanceY = abs(j - targetY)

        distance = np.sqrt(distanceX**2 + distanceY**2)
        return distance
        

    def FindMaxDistanceFromOrigin(self):
        maxDistance = 0

        i = 0
        while i < len(self.grid):
            j = 0
            while j < len(self.grid[i]):

                if self.grid[i][j] != 0:

                    distance = self.FindCellDistance(i, j, floor(len(self.grid[0])/2), floor(len(self.grid[:,0])/2))

                    if distance > maxDistance:
                        maxDistance = distance

                j += 1
            i += 1

        return maxDistance

    
    def AddRandomCell(self):

        placementRange = floor(self.FindMaxDistanceFromOrigin() + 2)
        
        if placementRange >= len(self.grid[0]) / 2:
            print("Placement circle outside of grid")
            return

        # Find all possible locations
        possibleCoordinates = []

        i = 0
        while i < len(self.grid):
            j = 0
            while j < len(self.grid[i]):

                cellDistance = self.FindCellDistance(i, j, floor(len(self.grid[0])/2), floor(len(self.grid[:,0])/2))
                if (cellDistance < placementRange + 1) and (cellDistance > placementRange - 1):
                    possibleCoordinates.append((i, j))

                j += 1
            i += 1

        # Select psudo random cell
        chosenCellCoords = random.choice(possibleCoordinates)

        self.PerformCellWalk(chosenCellCoords)

    
    def PerformCellWalk(self, initialCoordinates):

        # Test if cell too far away
        originDistance = self.FindCellDistance(initialCoordinates[0], initialCoordinates[1], floor(len(self.grid[0])/2), floor(len(self.grid[:,0])/2)) 
        rMax = self.FindMaxDistanceFromOrigin()
        if originDistance > 2*rMax + 2:
            #print(f"Cell too far, {originDistance} / {2*self.FindMaxDistanceFromOrigin() + 2}")
            self.AddRandomCell()
            return

        # Determine if adjacent to another cell
        i = 0
        searching = True
        while (i < len(self.grid)) and (searching is True):
            j = 0
            while j < len(self.grid[i]):

                if self.grid[i][j] >= 1:
                    if self.FindCellDistance(i, j, initialCoordinates[0], initialCoordinates[1]) == 1:
                        adjacent = True
                        searching = False
                        break
                else:
                    adjacent = False

                j += 1
            i += 1

        if adjacent is False:
            # Chose direction
            movement = self.ChooseRandomDirection(initialCoordinates, originDistance, rMax)

            # Do movement and repeat
            newCoordinates = (initialCoordinates[0] + movement[0], initialCoordinates[1] + movement[1])

            # check if new position is outside bounds

            #print(f"Current pos: {initialCoordinates}, New pos: {newCoordinates}", end="\r")

            self.PerformCellWalk(newCoordinates)

        else:
            self.grid[initialCoordinates[0]][initialCoordinates[1]] = 1


    def ChooseRandomDirection(self, currentPosition, originDistance, rMax):
        randomDirection = random.randint(0, 3) # starting from positive x and moving clockwise

        match randomDirection:
            case 0:
                movement = (1, 0)
            case 1:
                movement = (0, -1)
            case 2:
                movement = (-1, 0)
            case 3:
                movement = (0, 1)

        moveSpeed = 1

        if originDistance > rMax:
            moveSpeed = originDistance - rMax -1
        if moveSpeed < 1:
            moveSpeed = 1

        movement = [floor(el * moveSpeed) for el in movement]


        if (currentPosition[0] + movement[0] < 0) or (currentPosition[0] + movement[0] > len(self.grid[0]) -1):
            movement = self.ChooseRandomDirection(currentPosition, originDistance, rMax)
            return movement
        if (currentPosition[1] + movement[1] < 0) or (currentPosition[1] + movement[1] > len(self.grid[:,0]) -1):
            movement = self.ChooseRandomDirection(currentPosition, originDistance, rMax)
            return movement

        return movement


    def AgeCells(self):
        i = 0
        while i < len(self.grid):
            j = 0
            while j < len(self.grid[i]):

                if self.grid[i][j] > 0:
                    self.grid[i][j] += 1

                j += 1
            i += 1


def GetPlacementProbability(steps):

    gridSizeX = gridSizeY = 32
    origin = (floor(gridSizeX / 2), floor(gridSizeY / 2))

    rectLattice = Grid("Rectangular Lattice")

    probabilityGrid = Grid("Probability")
    probabilityGrid.InstantiateGrid(gridSizeX, gridSizeY)


    print("Testing probabilities")
    for n in tqdm(range(steps)):

        # Reset Grid
        rectLattice.InstantiateGrid(gridSizeX, gridSizeY)

        # Create Origin
        rectLattice.SetCell(origin[0], origin[1], 1)
        rectLattice.AgeCells()
        
        # Set up intial state
        rectLattice.SetCell(origin[0] + 1, origin[1], 1)


        # Add Random Cell
        rectLattice.AgeCells()
        rectLattice.AddRandomCell()


        probabilityGrid.grid += rectLattice.grid

    probabilityGrid.SetCell(origin[0], origin[1], 0)
    probabilityGrid.SetCell(origin[0] + 1, origin[1], 0)

    i = 0
    while i < len(probabilityGrid.grid[0]):
        j = 0
        while j < len(probabilityGrid.grid[:,0]):

            if probabilityGrid.grid[i][j] != 0:
                probabilityGrid.grid[i][j] /= steps 

            j += 1
        i += 1


    probabilityGrid.PlotGrid((10, 10), makeNan=True)

    plt.show()

    return

if __name__ == "__main__":
    main()
