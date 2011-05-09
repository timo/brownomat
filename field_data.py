testfielddata = """\
          ##    ##               ##
 ##O####O##############O######O#####
          #     #                ###
                                  #
                                  #
          #                  ##  ###
          #          ###############
         ##                   #  ##
         ###
          #    #
  #O###O###O######    ##
          #    #############
          #    ###    #
  #O###O##########      ##
          #    #################
          #      #      #
          #
          #
          #
         ###
        # # #   ##
   O#O#### ###O####
        # # #   ###
         ###     #
          #     ##
          #     ###
          #      #
         ###    ###
         ##########
          ##    ##
"""

c22join = """\
            #  #  #
            #  #  #
            #  #  #
            #  #  #
            # ### #
           ##  ## ##
           ### # ###
          # # ### # #
         ### ##### ###
        ### # ### # ###
      ## # ###   ### # ##
#############     ############
       # # #       # # #
     ## ###         ### ##  
##O########         ##########
     #  ###         ###  #  
       # # #       # # #    
#############     ############
      ## # ###   ### # ##
        ### # ### # ###
         ### ##### ###
          # # ### # #
           ### # ###
           ##  ## ##
            # ### #
            #  #  #
            #  #  #
            #  O  #
            #  #  #

"""

drjoin = """\
             c     r     d
             #     #     #
             #     #     #
             #     #     #
 a    #  ### # ### # ### # ###  #    b
############# ##### ##### ##############
      ## ### # ### # ### # ### ##
#################  #  ##################
 a'   #  ### ###   #   ### ###  #    b'
             #     #     #
             #     #     #
             c'    r'    d'
"""

# r merge d' merge c = c'
# c' merge d = c0
# r' = c1

# a0 -> a
# a1 -> b
# b0 -> a'
# b1 -> b'

xor_drjoin = """\


                      
         ##          ##   ## ##
        ########################
        ###           #    # ###
         #        ##   ###    #  ##   ##
         #       ########################
         #       ###   ###    #  #    ###
        ###       #     #     #        #
        ##       ##     ##    #        #
         #       ###   ###    #       ### ##  c'
         #        #     #     #       ###########
         #    ### # ### # ### # ###   ### #
         #    #### #### # #### ####    #
         # #  ### # ### # ### # ###  # #
  a0 ############ # #### #### # #########O### a1
         # ## ### # ### # ### # ### ## #
  b0 #################  #  ##############O### b1
         # #  ### ###   #   ### ###  # #
         #        #    ###    #        #
        ###       #    ##    ###   ## ###
        ##        #     #    ############
         #        #     #     ##   #  ##
        ### ###  ###    #
        ############    #
         ## ###  ##     #
             #          #
            ###         #
            ##          #
             #          #
             #          #
             #          #
         c0  #       c1 #

"""
