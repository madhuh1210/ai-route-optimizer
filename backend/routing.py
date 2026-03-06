from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2


def optimize_route(distance_matrix, num_vehicles=3):

    depot = 0
    max_orders_per_truck = 8

    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix),
        num_vehicles,
        depot
    )

    routing = pywrapcp.RoutingModel(manager)

    # -----------------------------
    # Distance callback
    # -----------------------------

    def distance_callback(from_index, to_index):

        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        return int(distance_matrix[from_node][to_node])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # -----------------------------
    # Demand callback (each order = 1)
    # -----------------------------

    def demand_callback(from_index):

        node = manager.IndexToNode(from_index)

        if node == 0:
            return 0

        return 1

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        [max_orders_per_truck] * num_vehicles,
        True,
        "Capacity"
    )

    # -----------------------------
    # Encourage using multiple trucks
    # -----------------------------

    for vehicle in range(num_vehicles):

        routing.SetFixedCostOfVehicle(1000, vehicle)

    # -----------------------------
    # Solver settings
    # -----------------------------

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()

    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    )

    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )

    search_parameters.time_limit.seconds = 5

    solution = routing.SolveWithParameters(search_parameters)

    routes = []

    if solution:

        for vehicle_id in range(num_vehicles):

            index = routing.Start(vehicle_id)

            vehicle_route = []

            while not routing.IsEnd(index):

                node = manager.IndexToNode(index)

                if node != 0:
                    vehicle_route.append(node)

                index = solution.Value(routing.NextVar(index))

            routes.append(vehicle_route)

    return routes