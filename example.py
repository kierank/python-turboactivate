#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from turboactivate import (
    TurboActivate,
    IsGenuineResult,
    TurboActivateError
)

import sys

# TODO: paste your Version GUID here.
TA_GUID = "18324776654b3946fc44a5f3.49025204"

# TODO: paste the path to your dat file here
TA_DAT_PATH = "TurboActivate.dat"

# Don't use 0 for either of these values.
# We recommend 90, 14. But if you want to lower the values
#  we don't recommend going below 7 days for each value.
# Anything lower and you're just punishing legit users.
DAYS_BETWEEN_CHECKS = 90
GRACE_PERIOD_LENGTH = 14

if __name__ == "__main__":

    # support both Python 2 and 3
    # for this simple example app
    try:
        input = raw_input
    except NameError:
        pass

    # now begins the licensing bit of the code
    isGenuine = False
    trial_days = 0

    try:
        ta = TurboActivate(TA_DAT_PATH, TA_GUID)

        # Check if we're activated, and every 90 days verify it with the activation servers
        # In this example we won't show an error if the activation was done offline
        # (see the 3rd parameter of the IsGenuine() function)
        # https://wyday.com/limelm/help/offline-activation/
        gen_r = ta.is_genuine_ex(DAYS_BETWEEN_CHECKS, GRACE_PERIOD_LENGTH, True)

        isGenuine = (gen_r == IsGenuineResult.Genuine
                     or gen_r == IsGenuineResult.GenuineFeaturesChanged

                     # an internet error means the user is activated but
                     # TurboActivate failed to contact the LimeLM servers
                     or gen_r == IsGenuineResult.InternetError
                     )

        if isGenuine:
            print('YourApp is activated and genuine! Enable any app features now.')
        elif not isGenuine and ta.is_activated():

            # There is still activation data on the computer, and it's valid.

            # This means that IsGenuineEx() is saying "not activated" (a.k.a. TA_FAIL)
            # because the customer blocked connections to the activation servers (intentionally or not)
            # for nDaysBetweenChecks + nGraceDaysOnInetErr days.

            # What you should do now is prompt the user telling them before they can use your app that they need
            # to reverify with the activation servers.

            print('You must reverify with the activation servers before you can use this app. ')
            print('Type R and then press enter to retry after you\'ve ensured that you\'re connected to the internet. ')
            print('Or to exit the app press X. ')

            while True:
                user_resp = sys.stdin.read(1)

                if user_resp == 'x' or user_resp == 'X':
                    sys.exit("Exiting now. Bye.")

                if user_resp == 'r' or user_resp == 'R':
                    # Now we're using TA_IsGenuine() to retry immediately. Note that we're not using
                    # TA_IsGenuineEx() because TA_IsGenuineEx() waits 5 hours after an internet failure
                    # before retrying to contact the servers. TA_IsGenuine() retries immediately.
                    igr = ta.is_genuine()

                    if igr == IsGenuineResult.Genuine or igr == IsGenuineResult.GenuineFeaturesChanged:
                        print('Successfully reverified with the servers! You can now continue to use the app!')
                        break
                    else:
                        print('Failed to reverify with the servers. ')
                        print('Make sure you\'re connected to the internet and that you\'re not blocking access to the activation servers. ')
                        print('Then press R to retry again. ')
                else:
                    print('Invalid input. Press R to try to reverify with the servers. Press X to exit the app.')

    except TurboActivateError as e:
        sys.exit("Failed to check if activated: " + str(e))



    # Get the number of trial days remaining and print them
    if not isGenuine:
        try:
            # Start or re-validate the trial if it has already started.
            # This need to be called at least once before you can use
            # any other trial functions.
            ta.use_trial(True)

            # Get the number of trial days remaining.
            trial_days = ta.trial_days_remaining()

            if trial_days > 0:
                print("Trial days remaining %d" % trial_days)
            else:
                print("There are no trial days remaining. You must activate now to continue to use this app.")
        except TurboActivateError as e:
            print("Failed to start the trial: " + str(e))




    # Whether to prompt for the product key
    prompt_for_key = False

    if not isGenuine:
        # ask the user if they want to enter their pkey
        print('Would you like to enter your pkey (y/n) [n]: ')
        prompt_res = sys.stdin.read(1)

        if prompt_res != "" and prompt_res == "y":
            prompt_for_key = True
        else:
            prompt_for_key = False

    # Now actually prompt for the product key and try to activate
    if prompt_for_key:
        try:
            # prompt the user for a product key
            pkey = input('Enter your product key to activate: ')

            ta.check_and_save_pkey(pkey)

            print("Product key saved successfully.")

        except TurboActivateError as e:
            sys.exit("Product key was not valid for this product version: " + str(e))

        # try to activate the product key
        try:
            ta.activate()

            isGenuine = True
            print("Activated successfully!")

        except TurboActivateError as e:
            sys.exit("Failed to activate online: " + str(e))

    # Prevent the user from going any further if they're not activated.
    if not isGenuine and trial_days == 0:
        sys.exit("You're not activated and there are no more trial days. You must activate to use this app.")

    # The customer is activated or is in trial mode!
    # From this point on is the "meat" of your app.

    # if this app is activated then you can get a feature value (completely optional)
    # See: https://wyday.com/limelm/help/license-features/
    #
    # feature_value = ta.get_feature_value("myFeature")
    # print("the value of myFeature is %s" % feature_value)

    print("Hello world!")