# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s collective.fancybox -t test_lightbox.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src collective.fancybox.testing.COLLECTIVE_FANCYBOX_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/collective/fancybox/tests/robot/test_lightbox.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a Lightbox
  Given a logged-in site administrator
    and an add Lightbox form
   When I type 'My Lightbox' into the title field
    and I submit the form
   Then a Lightbox with the title 'My Lightbox' has been created

Scenario: As a site administrator I can view a Lightbox
  Given a logged-in site administrator
    and a Lightbox 'My Lightbox'
   When I go to the Lightbox view
   Then I can see the Lightbox title 'My Lightbox'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Lightbox form
  Go To  ${PLONE_URL}/++add++Lightbox

a Lightbox 'My Lightbox'
  Create content  type=Lightbox  id=my-lightbox  title=My Lightbox

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Lightbox view
  Go To  ${PLONE_URL}/my-lightbox
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Lightbox with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Lightbox title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
