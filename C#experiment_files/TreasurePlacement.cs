// This script controls the location of the object attached to it
// Typically this will be a treasure in the unity environment

// To run, attach this c# script to the unity game object. \

// Note that building locations are hard coded into this script to prevent the
// treasure to be placed in a building

// Libraries
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using RosSharp.RosBridgeClient;

public class TreasurePlacement : MonoBehaviour
{
    // Define global variables
    // Change these variables to tune the game
    // [SerializeField] makes them accessable from unity
    [SerializeField]
    private Transform player;

    readonly private int distance_to_find_treasure = 1; // Distance from player for the player to get the treasure
    readonly private int initialize_dist_to_player = 25;

    // Initialize list to fill with building locations
    // private int[,] building_array = new int[30, 30];

    private float constantY;
    static public int treasureCount = 0;

    private List<int> bld_locations_x = new List<int>();
    private List<int> bld_locations_z = new List<int>();

    // Start is called before the first frame update
    private void Start()
    {
        populate_buildings(); // Adds coordinates of buildings to list

        constantY = transform.position.y; // Set the constantY to what it is at the beginning

        initialize_treasure();
    }

    // Update is called once per frame
    private void Update()
    {
        Vector3 vector_to_player = player.position - transform.position;
        double distance_temp = Math.Sqrt(Math.Pow((transform.position.x - player.position.x), 2) + Math.Pow((transform.position.z - player.position.z), 2));
        if (distance_temp<distance_to_find_treasure)
        {
            treasureCount += 1;
            //TreasureInfoPublisher.isTreasureFound = true;
            initialize_treasure();
        }
    }

    // This function places the player at a random point on the grid in which
    // the player is a certain distance away.
    private void initialize_treasure()
    {
        Debug.Log("Initializing treasure");
        bool starting_position_okay = false;
        System.Random rnd = new System.Random();
        int x_loc, z_loc;
        while (starting_position_okay == false)
        {
            // Choose random point on grid
            x_loc = rnd.Next(1, 29);
            z_loc = rnd.Next(1, 29);

            double distance_temp = Math.Sqrt(Math.Pow((x_loc + 0.5 - player.position.x), 2) + Math.Pow((z_loc + 0.5 - player.position.z), 2));  // float distance_temp = Vector3.Distance(patrol_goal_temp, transform.position);
            //Debug.Log("try distance " + distance_temp);
            if (distance_temp > initialize_dist_to_player)
            {
                bool isonbuilding = checkposition(x_loc, z_loc);

                if (isonbuilding == false){
                    //Debug.Log("Moving the treasure to a new location");
                    transform.position = new Vector3((float)(x_loc + 0.5), constantY, (float)(z_loc + 0.5));
                    starting_position_okay = true;
                }
            }
        }
    }

    // This function checks if there is a building at a specific grid point
    private bool checkposition(int x, int z)
    {
        bool isonbuilding = false;

        if (x > 29) { isonbuilding = true; }
        if (z > 29) { isonbuilding = true; }
        if (x < 0) { isonbuilding = true; }
        if (z < 0) { isonbuilding = true; }

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
