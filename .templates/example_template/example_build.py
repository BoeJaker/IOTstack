#!/usr/bin/env python3

issues = {} # Returned issues dict
buildHooks = {} # Options, and others hooks
haltOnErrors = True

# Main wrapper function. Required to make local vars work correctly
def main():
  from blessed import Terminal
  import types
  import time

  global dockerComposeYaml # The loaded memory YAML of all checked services
  global toRun # Switch for which function to run when executed
  global buildHooks # Where to place the options menu result
  global currentServiceName # Name of the current service
  global issues # Returned issues dict
  global haltOnErrors # Turn on to allow erroring

  # runtime vars
  portConflicts = []

  # This lets the menu know whether to put " >> Options " or not
  # This function is REQUIRED.
  def checkForOptionsHook():
    try:
      buildHooks["options"] = callable(runOptionsMenu)
    except:
      buildHooks["options"] = False
      return buildHooks
    return buildHooks

  # This function is REQUIRED.
  def checkForPreBuildHook():
    try:
      buildHooks["preBuildHook"] = callable(preBuild)
    except:
      buildHooks["preBuildHook"] = False
      return buildHooks
    return buildHooks

  # This function is REQUIRED.
  def checkForPostBuildHook():
    try:
      buildHooks["postBuildHook"] = callable(postBuild)
    except:
      buildHooks["postBuildHook"] = False
      return buildHooks
    return buildHooks

  # This function is REQUIRED.
  def checkForRunChecksHook():
    try:
      buildHooks["runChecksHook"] = callable(checkForIssues)
    except:
      buildHooks["runChecksHook"] = False
      return buildHooks
    return buildHooks

  # This service will not check anything unless this is set
  # This function is optional, and will run each time the menu is rendered
  def runChecks():
    checkForIssues()
    return []

  # This is the menu that will run for " >> Options "
  def runOptionsMenu():
    menuEntryPoint()
    return True

  # This function is optional, and will run after the docker-compose.yml file is written to disk.
  def postBuild():
    return True

  # This function is optional, and will run just before the build docker-compose.yml code.
  def preBuild():
    return True

  # #####################################
  # Supporting functions below
  # #####################################

  def checkForIssues():
    for (index, serviceName) in enumerate(dockerComposeYaml):
      if not currentServiceName == serviceName: # Skip self
        currentServicePorts = getExternalPorts(currentServiceName)
        portConflicts = checkPortConflicts(serviceName, currentServicePorts)
        if (len(portConflicts) > 0):
          issues["portConflicts"] = portConflicts

  def getExternalPorts(serviceName):
    externalPorts = []
    try:
      yamlService = dockerComposeYaml[serviceName]
      if "ports" in yamlService:
        for (index, port) in enumerate(yamlService["ports"]):
          try:
            externalAndInternal = port.split(":")
            externalPorts.append(externalAndInternal[0])
          except:
            pass
    except:
      pass
    return externalPorts

  def checkPortConflicts(serviceName, currentPorts):
    portConflicts = []
    if not currentServiceName == serviceName:
      yamlService = dockerComposeYaml[serviceName]
      servicePorts = getExternalPorts(serviceName)
      for (index, servicePort) in enumerate(servicePorts):
        for (index, currentPort) in enumerate(currentPorts):
          if (servicePort == currentPort):
            portConflicts.append([servicePort, serviceName])
    return portConflicts



  # #####################################
  # Example menu below
  # #####################################
  # You can build your menu system anyway you like. This one is provided as an example.
  # Checkout Blessed for full functionality, like text entry and so on at: https://blessed.readthedocs.io/en/latest/

  # The functions the menu executes are below. They must be placed before the menu list 'menuItemsExample'
  def menuCmdItem1():
    print("You chose item1!")
    return True

  def menuCmdAnotherItem():
    print("This is another menu item")
    return True

  def nop():
    return True

  def menuCmdStillAnotherItem():
    print("This is still another menu item")
    return True

  def goBack():
    global selectionInProgress
    selectionInProgress = False
    return True

  # The actual menu
  menuItemsExample = [
    ["Item 1", menuCmdItem1],
    ["Another item", menuCmdAnotherItem],
    ["I'm skipped!", nop, { "skip": True }],
    ["Still another item", menuCmdStillAnotherItem],
    ["Error item"],
    ["Error item"],
    ["Some custom thing", nop, { "customProperty": True }],
    ["I'm also skipped!", nop, { "skip": True }],
    ["Go back", goBack]
  ]

  # Vars that the menu uses
  global currentMenuItemIndex
  global selectionInProgress
  global menuNavigateDirection
  global needsRender

  selectionInProgress = True
  currentMenuItemIndex = 0
  menuNavigateDirection = 0
  needsRender = True

  # This is the main rendering function for the menu
  def mainRender(menu, selection):
    term = Terminal()
    print(term.clear())

    print(term.clear())
    print(term.move_y(term.height // 16))
    print(term.black_on_cornsilk4(term.center('IOTstack Example Commands')))
    print("")
    print(term.center("╔════════════════════════════════════════════════════════════════════════════════╗"))
    print(term.center("║                                                                                ║"))
    print(term.center("║      Select Command to run                                                     ║"))
    print(term.center("║                                                                                ║"))

    lineLengthAtTextStart = 75

    for (index, menuItem) in enumerate(menu):
      toPrint = ""
      if index == selection: # This checks if the current rendering item is the one that's selected
        toPrint += ('║   {t.blue_on_green} {title} {t.normal}'.format(t=term, title=menuItem[0]))
      else:
        if len(menu[index]) > 2 and "customProperty" in menu[index][2] and menu[index][2]["customProperty"] == True: # A custom property check
          toPrint += ('║   {t.black_on_green} {title} {t.normal}'.format(t=term, title=menuItem[0]))
        else:
          toPrint += ('║   {t.normal} {title} '.format(t=term, title=menuItem[0]))

      for i in range(lineLengthAtTextStart - len(menuItem[0])): # Pad the remainder of the line
        toPrint += " "

      toPrint += "║"

      toPrint = term.center(toPrint)
      
      print(toPrint)

    print(term.center("║                                                                                ║"))
    print(term.center("║                                                                                ║"))
    print(term.center("║      Controls:                                                                 ║"))
    print(term.center("║      [Up] and [Down] to move selection cursor                                  ║"))
    print(term.center("║      [Enter] to run command                                                    ║"))
    print(term.center("║      [Escape] to go back to main menu                                          ║"))
    print(term.center("║                                                                                ║"))
    print(term.center("║                                                                                ║"))
    print(term.center("╚════════════════════════════════════════════════════════════════════════════════╝"))


  def runSelection(selection):
    term = Terminal()
    if len(menuItemsExample[selection]) > 1 and isinstance(menuItemsExample[selection][1], types.FunctionType):
      menuItemsExample[selection][1]()
    else:
      print(term.green_reverse('IOTstack Example Error: No function assigned to menu item: "{}"'.format(menuItemsExample[selection][0])))

  def isMenuItemSelectable(menu, index):
    if len(menu) > index:
      if len(menu[index]) > 2:
        if "skip" in menu[index][2] and menu[index][2]["skip"] == True:
          return False
    return True

  def menuEntryPoint():
    # These need to be reglobalised due to eval()
    global currentMenuItemIndex
    global selectionInProgress
    global menuNavigateDirection
    global needsRender
    term = Terminal()
    with term.fullscreen():
      menuNavigateDirection = 0
      mainRender(menuItemsExample, currentMenuItemIndex)
      selectionInProgress = True
      with term.cbreak():
        while selectionInProgress:
          menuNavigateDirection = 0

          if needsRender: # Only rerender when changed to prevent flickering
            mainRender(menuItemsExample, currentMenuItemIndex)
            needsRender = False

          key = term.inkey()
          if key.is_sequence:
            if key.name == 'KEY_TAB':
              menuNavigateDirection += 1
            if key.name == 'KEY_DOWN':
              menuNavigateDirection += 1
            if key.name == 'KEY_UP':
              menuNavigateDirection -= 1
            if key.name == 'KEY_ENTER':
              runSelection(currentMenuItemIndex)
            if key.name == 'KEY_ESCAPE':
              return True
          elif key:
            print("got {0}.".format(key))

          if menuNavigateDirection != 0: # If a direction was pressed, find next selectable item
            currentMenuItemIndex += menuNavigateDirection
            currentMenuItemIndex = currentMenuItemIndex % len(menuItemsExample)
            needsRender = True

            while not isMenuItemSelectable(menuItemsExample, currentMenuItemIndex):
              currentMenuItemIndex += menuNavigateDirection
              currentMenuItemIndex = currentMenuItemIndex % len(menuItemsExample)
    return True





  # Entrypoint for execution
  if haltOnErrors:
    eval(toRun)()
  else:
    try:
      eval(toRun)()
    except:
      pass

# This check isn't required, but placed here for debugging purposes
global currentServiceName # Name of the current service
if currentServiceName == 'SERVICENAME':
  main()
else:
  print("Error. '{}' Tried to run 'SERVICENAME' config".format(currentServiceName))