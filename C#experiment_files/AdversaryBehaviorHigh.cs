
// This script...

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AdversaryBehaviorHigh : MonoBehaviour
{
    // Define global variables
    // Change these variables to tune the game
    // [SerializeField] makes them accessable from unity
    [SerializeField]
    private Transform player;

    public static float walkSpeed = 0.1f;
    readonly private float rotSpeed = 4f;

    // The adversary number (0,1,or 2) defines the resting patrol route
    // Adversary 0's route covers z-coordinates 0-9
    // Adversary 0's route covers z-coordinates 10-19
    // Adversary 0's route covers z-coordinates 20-19
    [SerializeField]
    private int adversary_number = 0;

    // How many grid squares to chase player without seeing player - note that
    // this is the same thing as specifying a max time to chase the player since
    // the adversary moves at a constant speed
    readonly private int max_distance_chase = 10;

    //[SerializeField]
    //public int lives = 3; // Number of lives in the game
    readonly private int distance_to_loose_life = 2; // Distance from player for the player to loose a life
    readonly private int initialize_dist_to_player = 15;
    readonly private double line_of_sight = 10;

    // Define remaining global variables
    // Define patrol route on unity grid
    private int[] patrol_x = { 2, 2, 2, 3, 3, 3, 4, 5, 6, 6, 6, 6, 6, // red
                              7, 7, 7, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, // blue
                              16, 16, 16, 17, 17, 17, 18, 19, 20, 21, 22, 22, 22, 22, 22, // red
                              23, 23, 23, 23, 24, 25, 26, 27, 28, 29, 29, 28, 27, // blue
                              27, 27, 27, 27, 27, 27, 27, 26, 26, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, // red
                              17, 17, 17, 17, 16, 16, 16, 16, 15, 14, 13, 13, 13, 13, // blue
                              12, 12, 12, 12, 12, 11, 10, 9, 8, 7, 7, 7, // red
                              6, 6, 6, 5, 4, 3, 2, 1, 0, 0, 1, 2, 2, 2, 2};
    private int[] patrol_z = { 2, 1, 0, 0, 1, 2, 2, 2, 2, 3, 4, 5, 6, // red
                              6, 5, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, // blue
                              2, 1, 0, 0, 1, 2, 2, 2, 2, 2, 2, 3, 4, 5, 6, // red
                              6, 5, 4, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, // blue
                              3, 4, 5, 6, 7, 8, 9, 9, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, // red
                              6, 5, 4, 3, 3, 4, 5, 6, 6, 6, 6, 5, 4, 3, // blue
                              3, 4, 5, 6, 7, 7, 7, 7, 7, 7, 8, 9, // red
                              9, 8, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 5, 4, 3 };
    private int patrol_index;
    Vector3 patrol_goal_position;

    // Initialize variables for goal locations
    private int goal_x;
    private int goal_z;

    // Variables holding the goal walking vector_to_goal and rotation_to_goal for command in Update()
    private Vector3 target;
    private Vector3 vector_to_goal;
    private Quaternion rotation_to_goal;
    private float constantY; // The y-position should not change from start

    // Initialize list to fill with building locations
    // private int[,] building_array = new int[30, 30];
    private List<int> bld_locations_x = new List<int>();
    private List<int> bld_locations_z = new List<int>();

    private int chase; // Chase the player until this value is equal to max_distance_chase
                       // the value is increased every time a goal is set
    private bool returntopatrol;

    // Intialize animator
    private Animator anim;

    // Start is called before the first frame update
    private void Start()
    {
        // Get the animator components attached to the game object
        anim = GetComponent<Animator>();

        // Set the adversary to walking position, always.
        anim.SetBool("isIdle", false);
        anim.SetBool("isWalking", true);

        populate_buildings(); // Adds coordinates of buildings to list

        constantY = transform.position.y; // Set the constantY to what it is at the beginning

        // Edit patrol route according to adversary_number
        if (adversary_number == 1)
        {
            for (int i = 0; i < patrol_x.Length; i++)
            {
                //patrol_x[i] = patrol_x[i] + 10;
                patrol_z[i] = patrol_z[i] + 10;
            }
        }
        else if (adversary_number == 2)
        {
            for (int i = 0; i < patrol_x.Length; i++)
            {
                //patrol_x[i] = patrol_x[i] + 20;
                patrol_z[i] = patrol_z[i] + 20;
            }
        }

        initialize_adversary();
    }

    // Update is called once per frame
    private void Update()
    {

        // Conditions for setting a new goal
        // 1) The adversary has reached the existing goal
        // 2) The adversary spots the player

        // Check if the player is within sight
        // If too slow, only check when the goal has been reached
        Vector3 vector_to_player = player.position - transform.position;
        bool iswithinsight = checksight(vector_to_player);

        // If just spotted player, set new goal immediately
        if (iswithinsight)// && (chase > 0))
        {
            //Debug.Log("I see you... "); //Spotted player!");
            chase = 0;
            // Chose the grid space to go to that gets you closer to the player
            Vector3 next_goal = nextgoalgrid(goal_x, goal_z, player.position);
            goal_x = (int)Math.Floor(next_goal.x);
            goal_z = (int)Math.Floor(next_goal.z);
            returntopatrol = false; // if the person is returning to patrol, stop

            ////Uncomment for new version
            //float distance = next_goal.y;
            //if (distance < distance_to_loose_life)
            //{
            //    lives = lives - 1;
            //    //initialize_adversary();
            //}

            // Initialize movement to new goal: vector_to_goal and rotation_to_goal
            target = new Vector3((goal_x + 0.5f), constantY, (goal_z + 0.5f));
            vector_to_goal = target - transform.position;
            rotation_to_goal = Quaternion.LookRotation(vector_to_goal);
        }
        // Check is goal has been reached and set new one if is has been reached
        else
        {
            // Determine if the goal has been reached
            float goal_error = 0.1f; // Goal error allowed to for the person to be
                                     //considered having reached the goal
                                     // If the update rate is slow, this might need to be changed
            bool isreached = ((Math.Abs((goal_x + 0.5) - transform.position.x) < goal_error) &&
                                  (Math.Abs((goal_z + 0.5) - transform.position.z) < goal_error));
            // If reached, determine new goal and set new direction/rotation
            if (isreached)
            {
                // If chasing the person, pick a new goal that gets you closer
                if (chase < max_distance_chase)
                {
                    // Chose a new goal that gets you closer to the player
                    Vector3 next_goal = nextgoalgrid(goal_x, goal_z, player.position);
                    goal_x = (int)Math.Floor(next_goal.x);
                    goal_z = (int)Math.Floor(next_goal.z);
                    float distance = next_goal.y;
                    if (distance < distance_to_loose_life)
                    {
                        //Debug.Log("Oh NO - you lost a life!");
                        GameManager.lives -= 1;
                        //Debug.Log("Player now has only " + PlayerManager.lives + " lives left.");
                        initialize_adversary();
                    }
                    chase++;
                    // If the adversary has been chasing the player for long
                    // enough without seeing player, return to patrol
                    if (chase == max_distance_chase)
                    {
                        returntopatrol = true;
                        // Find closest point on patrol
                        double min_distance = 100000;
                        for (int i = 0; i == patrol_x.Length; i++)
                        {
                            double distance_temp = Math.Sqrt(Math.Pow((patrol_x[i] + 0.5 - transform.position.x), 2) + Math.Pow((patrol_z[i] + 0.5 - transform.position.z), 2));  // float distance_temp = Vector3.Distance(patrol_goal_temp, transform.position);
                            if (distance_temp < min_distance)
                            {
                                patrol_index = i;
                                min_distance = distance_temp;
                            }
                        }
                        patrol_goal_position = new Vector3(patrol_x[patrol_index], constantY, patrol_z[patrol_index]);
                        //Debug.Log("Returning to patrol position [x: " + patrol_x[patrol_index] + " z: " + patrol_z[patrol_index] + "].");
                    }
                }
                //Else, if returning to patrol, pick a new goal that gets you closer
                else if (returntopatrol == true)
                {
                    // Find next goal that gets the adversary closer to the patrol_goal_position
                    Vector3 next_goal = nextgoalgrid(goal_x, goal_z, patrol_goal_position);
                    goal_x = (int)Math.Floor(next_goal.x);
                    goal_z = (int)Math.Floor(next_goal.z);
                    float distance = next_goal.y;
                    // If this goal gets you back on route, you no longer need to return to patrol
                    if (distance < 1.1)
                    {
                        returntopatrol = false;
                        //Debug.Log("Back on patrol route.");
                    }
                }
                // Otherwise, continue on patrol
                else
                {
                    // The patrol is one big loop. If the adversary has reached
                    // the end of the array, begin at the beginning again
                    if (patrol_index >= patrol_x.Length) { patrol_index = 0; }
                    else { patrol_index++; }
                    goal_x = patrol_x[patrol_index];
                    goal_z = patrol_z[patrol_index];
                }
                // Initialize movement to new goal: vector_to_goal and rotation_to_goal
                target = new Vector3((goal_x + 0.5f), constantY, (goal_z + 0.5f));
                //Debug.Log("New goal [x: " + goal_x + ", z: " + goal_z + "] patrol_index: " + patrol_index + ".");
                vector_to_goal = target - transform.position;
                rotation_to_goal = Quaternion.LookRotation(vector_to_goal);
            }
        }

        // Move adversary a step
        float step = walkSpeed * Time.deltaTime;
        transform.position = Vector3.MoveTowards(transform.position, target, step);

        float rotstep = rotSpeed * Time.deltaTime;
        transform.rotation = Quaternion.Lerp(transform.rotation, rotation_to_goal, rotstep);
    }

    // This function places the player at a random point in the patrol in which
    // they cannot see the player and is a certain distance away.
    private void initialize_adversary()
    {

        chase = max_distance_chase; // Start not chasing player
        returntopatrol = false; // Start on patrol so there is no need to return to patrol

        bool starting_position_okay = false;
        System.Random rnd = new System.Random();
        while (starting_position_okay == false)
        {
            // Choose random point on patrol
            //Debug.Log("Try a new location.");
            patrol_index = rnd.Next(0, patrol_x.Length - 1);
            double distance_temp = Math.Sqrt(Math.Pow((patrol_x[patrol_index] + 0.5 - player.position.x), 2) + Math.Pow((patrol_z[patrol_index] + 0.5 - player.position.z), 2));  // float distance_temp = Vector3.Distance(patrol_goal_temp, transform.position);
            if (distance_temp > initialize_dist_to_player)
            {
                Vector3 vector_to_player = player.position - transform.position;
                bool iswithinsight = checksight(vector_to_player);
                if (iswithinsight == false) { starting_position_okay = true; }
            }
        }
        goal_x = patrol_x[patrol_index];
        goal_z = patrol_z[patrol_index];

        //Debug.Log("Bye bye... I'm moving to new position!");
        // Position the adversary to the new location
        transform.position = new Vector3((float)(goal_x + 0.5), constantY, (float)(goal_z + 0.5));

        // Initialize movement to new goal: vector_to_goal and rotation_to_goal
        target = new Vector3((float)patrol_x[patrol_index + 1] + .5f, constantY, (float)patrol_z[patrol_index + 1] + .5f);
        vector_to_goal = target - transform.position;
        rotation_to_goal = Quaternion.LookRotation(vector_to_goal);
    }

    // This function finds the next adjacent grid square that gets you closest
    // to the goal object without running into building. It also outputs the
    // distance to object at the y-coor
    private Vector3 nextgoalgrid(int current_goal_x, int current_goal_z, Vector3 object_of_interest)
    {
        // Initialize goal to current goal
        int goal_x_temp = current_goal_x;
        int goal_z_temp = current_goal_z;
        double min_distance = 100000;
        bool isonbuilding;
        // the indecies of the goal objects represent this: 0=+x 1=+y 2=-x 3=-y
        int[] goal_x_options = { current_goal_x + 1, current_goal_x, current_goal_x - 1, current_goal_x };
        int[] goal_z_options = { current_goal_z, current_goal_z + 1, current_goal_z, current_goal_z - 1 };
        // Check the nearby 4 grid squares to determine which is okay and brings you closer to the goal
        for (int i = 0; i < 4; i++)
        {
            isonbuilding = checkposition(goal_x_options[i], goal_z_options[i]);
            if (isonbuilding == false)
            {
                // Get distance to that goal
                double distance_temp = Math.Sqrt(Math.Pow((goal_x_options[i] + 0.5 - object_of_interest.x), 2) + Math.Pow((goal_z_options[i] + 0.5 - object_of_interest.z), 2));
                // If it is a better choice, set the new goal
                if (min_distance > distance_temp)
                {
                    goal_x_temp = goal_x_options[i];
                    goal_z_temp = goal_z_options[i];
                    min_distance = distance_temp;
                }
            }
        }
        Vector3 next_goal = new Vector3(goal_x_temp, (float)min_distance, goal_z_temp);
        return next_goal;
    }

    // This function checks if there is a building at a specific grid point
    private bool checkposition(int x, int z)
    {
        bool isonbuilding = false;

        if (x > 29) { x = 29; }
        if (z > 29) { z = 29; }
        if (x < 0) { x = 0; }
        if (z < 0) { z = 0; }

        // if (building_array[x, z] == 1)
        // {
        //     isonbuilding = true;
        // }
        int i = 0;
        int len = bld_locations_x.Count;
        // Stops if it has already found a building at that location
        while ((isonbuilding == false) && i < len)
        {
           if ((bld_locations_x[i] == x) && (bld_locations_z[i] == z))
           {
               isonbuilding = true;
           }
           i++;
        }
        return isonbuilding;
    }

    // This functio checks whether the adversary can see the player. It takes a
    // vector from the adversary to the player
    private bool checksight(Vector3 vector_to_player)
    {
        // Both of these need to be true for the the person to be in sight
        bool is_path_on_building = false;
        bool is_facing_player = false;
        bool is_within_line_of_sight = false;

        // Take dot product between vector to person and vector to next goal
        double dotproduct = Vector3.Dot(vector_to_goal.normalized, vector_to_player.normalized);
        if (dotproduct > (Math.Cos(3.14 / 4))) // Can see 45 degrees right and left
        {
            is_facing_player = true;
        }
        if (is_facing_player)
        {  // Only do this test is the first is true
            //Check to see if they are within line of sight
            double distance_temp = Math.Sqrt(Math.Pow((vector_to_player.x), 2) + Math.Pow((vector_to_player.z), 2));
            //Debug.Log("distance: " + distance_temp);
            if (distance_temp < line_of_sight)
            {
                //Debug.Log("The adversary is close and facing player.");
                is_within_line_of_sight = true;

                int num_tests = 100; // Check this many points along vector_to_player
                Vector3 vector_to_player_step = vector_to_player / num_tests;
                Vector3 prev_position = transform.position;
                Vector3 new_position;
                int i = 0;
                // Check the length of the vector for buildings; stop if found
                while ((is_path_on_building == false) && (i <= num_tests))
                {
                    new_position = prev_position + vector_to_player_step;
                    // Check for buildings only if you have entered a new grid space along the vector.
                    if ((Math.Floor(new_position.x) == Math.Floor(prev_position.x)) && (Math.Floor(new_position.z) == Math.Floor(prev_position.z)))
                    {
                    }
                    else
                    {
                        is_path_on_building = checkposition((int)Math.Floor(new_position.x), (int)Math.Floor(new_position.z));
                    }
                    prev_position = new_position;
                    i++;
                }
            }
        }

        bool iswithinsight = (is_facing_player && is_within_line_of_sight && (is_path_on_building == false));
        return (iswithinsight);
    }

    // This function hard-codes the grid spaces that contain a building
    private void populate_buildings()
    {
        // Add small buildings
        int[] bld_small_x_unity = {0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 1.1
                     0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 1.2
                     0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 2.1
                     0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 2.2
                     0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 5.1
                     0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 5.2
                     0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 8.1
                     0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 8.2
                     0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 9.1
                     0, 1, 4, 5, 14, 15, 24, 25, 28, 29}; // Row 9.2
        int[] bld_small_y_unity = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, // Row 1.1
                     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, // Row 1.2
                     4, 4, 4, 4, 4, 4, 4, 4, 4, 4, // Row 2.1
                     5, 5, 5, 5, 5, 5, 5, 5, 5, 5, // Row 2.2
                     14, 14, 14, 14, 14, 14, 14, 14, 14, 14, // Row 5.1
                     15, 15, 15, 15, 15, 15, 15, 15, 15, 15, // Row 5.1
                     24, 24, 24, 24, 24, 24, 24, 24, 24, 24, // Row 8.1
                     25, 25, 25, 25, 25, 25, 25, 25, 25, 25, // Row 8.2
                     28, 28, 28, 28, 28, 28, 28, 28, 28, 28, // Row 9.1
                     29, 29, 29, 29, 29, 29, 29, 29, 29, 29 }; // Row 9.2
                                                               // Add horizontal buildings
        int[] bld_2horiz_x_unity = {8, 9, 10, 11, 18, 19, 20, 21, // Row 1.1
                      8, 9, 10, 11, 18, 19, 20, 21, // Row 1.2
                      8, 9, 10, 11, 18, 19, 20, 21, // Row 2.1
                      8, 9, 10, 11, 18, 19, 20, 21, // Row 2.2
                      8, 9, 10, 11, 18, 19, 20, 21, // Row 5.1
                      8, 9, 10, 11, 18, 19, 20, 21, // Row 5.2
                      8, 9, 10, 11, 18, 19, 20, 21, // Row 8.1
                      8, 9, 10, 11, 18, 19, 20, 21, // Row 8.2
                      8, 9, 10, 11, 18, 19, 20, 21, // Row 9.1
                      8, 9, 10, 11, 18, 19, 20, 21 }; // Row 9.2
        int[] bld_2horiz_y_unity = {0, 0, 0, 0, 0, 0, 0, 0, // Row 1.1
                      1, 1, 1, 1, 1, 1, 1, 1, // Row 1.2
                      4, 4, 4, 4, 4, 4, 4, 4, // Row 2.1
                      5, 5, 5, 5, 5, 5, 5, 5, // Row 2.2
                     14, 14, 14, 14, 14, 14, 14, 14, // Row 5.1
                     15, 15, 15, 15, 15, 15, 15, 15, // Row 5.2
                     24, 24, 24, 24, 24, 24, 24, 24, // Row 8.1
                     25, 25, 25, 25, 25, 25, 25, 25, // Row 8.2
                     28, 28, 28, 28, 28, 28, 28, 28,  // Row 9.1
                     29, 29, 29, 29, 29, 29, 29, 29 }; // Row 9.2
                                                       // Add vertical buildings
        int[] bld_2vert_x_unity = {0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 3/4.1
                   0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 3/4.2
                   0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 3/4.3
                   0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 3/4.4
                   0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 6/7.1
                   0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 6/7.2
                   0, 1, 4, 5, 14, 15, 24, 25, 28, 29, // Row 6/7.3
                   0, 1, 4, 5, 14, 15, 24, 25, 28, 29 }; // Row 6/7.4
        int[] bld_2vert_y_unity = {8, 8, 8, 8, 8, 8, 8, 8, 8, 8, // Row 3/4.1
                   9, 9, 9, 9, 9, 9, 9, 9, 9, 9, // Row 3/4.2
                   10, 10, 10, 10, 10, 10, 10, 10, 10, 10, // Row 3/4.3
                   11, 11, 11, 11, 11, 11, 11, 11, 11, 11, // Row 3/4.4
                   18, 18, 18, 18, 18, 18, 18, 18, 18, 18, // Row 6/7.1
                   19, 19, 19, 19, 19, 19, 19, 19, 19, 19, // Row 6/7.2
                   20, 20, 20, 20, 20, 20, 20, 20, 20, 20, // Row 6/7.3
                   21, 21, 21, 21, 21, 21, 21, 21, 21, 21 // Row 6/7.4
                     };
        // Add large buildings
        int[] bld_large_x_unity = {8, 9, 10, 11, 18, 19, 20, 21,  // Row 3/4.1
                    8, 9, 10, 11, 18, 19, 20, 21,  // Row 3/4.2
                    8, 9, 10, 11, 18, 19, 20, 21,  // Row 3/4.3
                    8, 9, 10, 11, 18, 19, 20, 21,  // Row 3/4.4
                    8, 9, 10, 11, 18, 19, 20, 21,  // Row 6/7.1
                    8, 9, 10, 11, 18, 19, 20, 21,  // Row 6/7.2
                    8, 9, 10, 11, 18, 19, 20, 21,  // Row 6/7.3
                    8, 9, 10, 11, 18, 19, 20, 21 };  // Row 6/7.4
        int[] bld_large_y_unity = {8, 8, 8, 8, 8, 8, 8, 8,  // Row 3/4.1
                   9, 9, 9, 9, 9, 9, 9, 9, // Row 3/4.2
                   10, 10, 10, 10, 10, 10, 10, 10, // Row 3/4.3
                   11, 11, 11, 11, 11, 11, 11, 11, // Row 3/4.4
                   18, 18, 18, 18, 18, 18, 18, 18, // Row 6/7.1
                   19, 19, 19, 19, 19, 19, 19, 19, // Row 6/7.2
                   20, 20, 20, 20, 20, 20, 20, 20, // Row 6/7.3
                   21, 21, 21, 21, 21, 21, 21, 21 }; // Row 6/7.4
        for (int i = 0; i < bld_small_x_unity.Length; i++)
        {
            bld_locations_x.Add(bld_small_x_unity[i]);
            bld_locations_z.Add(bld_small_y_unity[i]);
        }
        for (int i = 0; i < bld_2horiz_x_unity.Length; i++)
        {
            bld_locations_x.Add(bld_2horiz_x_unity[i]);
            bld_locations_z.Add(bld_2horiz_y_unity[i]);
        }
        for (int i = 0; i < bld_2vert_x_unity.Length; i++)
        {
            bld_locations_x.Add(bld_2vert_x_unity[i]);
            bld_locations_z.Add(bld_2vert_y_unity[i]);
        }
        for (int i = 0; i < bld_large_x_unity.Length; i++)
        {
            bld_locations_x.Add(bld_large_x_unity[i]);
            bld_locations_z.Add(bld_large_y_unity[i]);
        }
      }
}
