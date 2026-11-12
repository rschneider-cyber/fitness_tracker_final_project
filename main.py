from dataclasses import dataclass
from drafter import *
from bakery import assert_equal

set_site_information(
    author="Ryan Schneider",
    description="A personal fitness tracker to log workouts and monitor daily goals.",
    sources=["Course lecture slides", "Drafter documentation", "LLM Assistant"],
    planning=["Week 10 Brainstorming Worksheet", "Week 11 Design Worksheet"],
    links=["github.com/rschneider-cyber/fitness_tracker_final_project"]
)

# Dataclass for workout entry and state of the app
@dataclass
class WorkoutEntry:
    name: str
    category: str
    duration: int
    calories: int
    is_favorite: bool

# Dataclass to store all WorkoutEntry instances and customizable user settings
# to pretty up and personalize the UI
@dataclass
class State:
    workouts: list[WorkoutEntry]
    daily_goal_minutes: int
    selected_category: str
    user_name: str
    fitness_focus: str
    motto: str


# Helper functions (mainly supports stats page) + homebar
def get_total_minutes(workouts: list[WorkoutEntry]) -> int:
    """Calculates total workout duration in minutes."""
    total = 0
    for workout in workouts:
        total += workout.duration
    return total

def get_total_calories(workouts: list[WorkoutEntry]) -> int:
    """Calculates total calories burned across all workouts."""
    total = 0
    for workout in workouts:
        total += workout.calories
    return total

def count_by_category(workouts: list[WorkoutEntry], category_name: str) -> int:
    """Counts how many workouts belong to a specific category."""
    count = 0
    for workout in workouts:
        if workout.category == category_name:
            count += 1
    return count

def make_navbar() -> list:
    """Returns a clean navigation bar present across pages."""
    return [
        Link("🏡 Home", index),
        Text("  |  "),

        Link("➕ Add Workout", show_add_workout),
        Text("  |  "),

        Link("📙 Log", show_log),
        Text("  |  "),

        Link("📊 Stats", show_stats),
        Text("  |  "),

        Link("🛠️ Settings", show_settings),
        LineBreak(),
        LineBreak()
    ]


# Home Dashboard Page (subject to change to make it prettier)
@route
def index(state: State) -> Page:
    """
    Displays a welcome message, user's fitness focus, motivational motto,
    and the day's progress towards the daily workout goal. It provides feedback
    on whether the user has met their goal and/or how much more to reach it.
    """
    total_mins = get_total_minutes(state.workouts)
    
    if total_mins >= state.daily_goal_minutes:
        goal_msg = "🎉 Great job! You hit your daily active workout goal!"
    else:
        remaining = state.daily_goal_minutes - total_mins
        goal_msg = f"💪 Keep pushing! You need {remaining} more minutes to reach your goal."

    return Page(state, [
        *make_navbar(),
        Header(f"Welcome back, {state.user_name}!"),
        Text(f"Focus Mode: {state.fitness_focus}"),
        LineBreak(),

        Text(f'Motto: "{state.motto}"'),
        LineBreak(),
        LineBreak(),

        Header("Today's Progress", level=2),
        Text(f"• Daily Goal: {state.daily_goal_minutes} mins"),
        LineBreak(),

        Text(f"• Total Logged Today: {total_mins} mins"),
        LineBreak(),
        LineBreak(),

        Text(goal_msg),
    ])


# Log workout page
@route
def show_add_workout(state: State) -> Page:
    """Log workout page: add workouts to list for tracking and stats."""
    return Page(state, [
        *make_navbar(),
        Header("Log a New Workout"),
        Text("Exercise Name:"),
        LineBreak(),

        TextBox("name", "Treadmill Run"),
        LineBreak(),
        LineBreak(),

        Text("Category:"),
        LineBreak(),

        SelectBox("category", ["Cardio", "Strength", "Flexibility", "Other"]),
        LineBreak(),
        LineBreak(),

        Text("Duration (minutes):"),
        LineBreak(),

        TextBox("duration", "30"),
        LineBreak(),
        LineBreak(),

        Text("Calories Burned:"),
        LineBreak(),

        TextBox("calories", "200"),
        LineBreak(),
        LineBreak(),

        Text("Mark as Favorite Workout:"),
        CheckBox("is_favorite", False),
        LineBreak(),
        LineBreak(),

        Button("Save Workout Session", add_workout_submit),
    ])


@route
def add_workout_submit(
    state: State, name: str, category: str, duration: str, calories: str, is_favorite: bool
) -> Page:
    """
    Checks for input sanitation and updates state if valid, or returns an error
    message if otherwise to prevent unreasonable values from being added to the
    workouts list.
    """
    dur_num = int(duration)
    cal_num = int(calories)

    if dur_num <= 0 or cal_num < 0:
        return Page(state, [
            *make_navbar(),
            Header("Input Error"),
            Text("⚠️ Duration must be greater than 0 and calories cannot be negative."),
            LineBreak(),
            LineBreak(),

            Link("Go Back & Correct", show_add_workout)
        ])

    new_entry = WorkoutEntry(name, category, dur_num, cal_num, is_favorite)
    state.workouts.append(new_entry)
    
    return index(state)


# Workout log display page
@route
def show_log(state: State) -> Page:
    """
    Workout log display page. Also allows the user to filter their logs by
    category and view favorite logs.
    """
    items = []
    
    for workout in state.workouts:
        if state.selected_category == "All" or workout.category == state.selected_category:
            fav_tag = " ⭐" if workout.is_favorite else ""
            entry_text = (
                f"• {workout.name} ({workout.category}) — "
                f"{workout.duration} mins | {workout.calories} cal{fav_tag}"
            )
            items.append(Text(entry_text))
            items.append(LineBreak())

    if not items:
        items = [Text("No workout records match this category."), LineBreak()]

    return Page(state, [
        *make_navbar(),
        Header("Workout Log"),
        Text(f"Filter by Category (Current: {state.selected_category}):"),
        LineBreak(),
        SelectBox("category_filter", ["All", "Cardio", "Strength", "Flexibility", "Other"]),
        Button("Apply Filter", filter_category),
        LineBreak(),
        LineBreak(),
        Header("Your Logged Activities", level=2),
        *items
    ])


@route
def filter_category(state: State, category_filter: str) -> Page:
    """Updates and refreshes the log based on the new filter selection."""
    state.selected_category = category_filter
    return show_log(state)


# Stats page
@route
def show_stats(state: State) -> Page:
    """
    Stats page. Shows: Total workout time, calories burned, session count,
    and category breakdown.
    """
    total_mins = get_total_minutes(state.workouts)
    total_cals = get_total_calories(state.workouts)
    count = len(state.workouts)
    
    avg_len = 0
    if count > 0:
        avg_len = total_mins // count

    cardio_count = count_by_category(state.workouts, "Cardio")
    strength_count = count_by_category(state.workouts, "Strength")
    flex_count = count_by_category(state.workouts, "Flexibility")

    return Page(state, [
        *make_navbar(),
        Header("Fitness Summary & Stats"),
        Header("Overview Metrics", level=2),
        Text(f"• Total Recorded Sessions: {count}"),
        LineBreak(),

        Text(f"• Total Time Exercising: {total_mins} minutes"),
        LineBreak(),

        Text(f"• Total Energy Burned: {total_cals} cal"),
        LineBreak(),

        Text(f"• Average Session Duration: {avg_len} minutes/session"),
        LineBreak(),
        LineBreak(),

        Header("Category Breakdown", level=2),
        Text(f"• Cardio Sessions: {cardio_count}"),
        LineBreak(),

        Text(f"• Strength Sessions: {strength_count}"),
        LineBreak(),

        Text(f"• Flexibility Sessions: {flex_count}"),
    ])


# Settings page
@route
def show_settings(state: State) -> Page:
    """
    Settings page. Allows the user to customize their profile and preferences,
    including name, fitness focus, motto, and daily target goal.
    """
    return Page(state, [
        *make_navbar(),
        Header("User Profile & Preferences"),
        Text("Your Name:"),
        LineBreak(),

        TextBox("user_name", state.user_name),
        LineBreak(),
        LineBreak(),

        Text("Primary Fitness Focus:"),
        LineBreak(),

        SelectBox("fitness_focus", ["General Health", "Weight Loss", "Muscle Building", "Endurance"]),
        LineBreak(),
        LineBreak(),

        Text("Motivational Motto / Goal Quote:"),
        LineBreak(),

        TextBox("motto", state.motto),
        LineBreak(),
        LineBreak(),

        Text("Daily Target Goal (Minutes):"),
        LineBreak(),

        TextBox("daily_goal", str(state.daily_goal_minutes)),
        LineBreak(),
        LineBreak(),

        Button("Save Profile & Settings", update_settings),
    ])


@route
def update_settings(
    state: State, user_name: str, fitness_focus: str, motto: str, daily_goal: str) -> Page:
    """Updates the webapp to reflect the new settings the user has selected."""
    state.user_name = user_name
    state.fitness_focus = fitness_focus
    state.motto = motto
    state.daily_goal_minutes = int(daily_goal)
    return index(state)


# Helper function tests - Skip to ~line 800 for server initialization

assert_equal(get_total_minutes([]), 0)
assert_equal(
    get_total_minutes([WorkoutEntry("Run", "Cardio", 30, 200, True)]),
    30
)
assert_equal(
    get_total_minutes([
        WorkoutEntry("Run", "Cardio", 30, 200, True),
        WorkoutEntry("Walk", "Cardio", 15, 80, False)
    ]),
    45
)
assert_equal(
    get_total_minutes([WorkoutEntry("Rest", "Other", 0, 0, False)]),
    0
)

assert_equal(get_total_calories([]), 0)
assert_equal(
    get_total_calories([WorkoutEntry("Run", "Cardio", 30, 200, True)]),
    200
)
assert_equal(
    get_total_calories([
        WorkoutEntry("Run", "Cardio", 30, 200, True),
        WorkoutEntry("Walk", "Cardio", 15, 80, False)
    ]),
    280
)
assert_equal(
    get_total_calories([WorkoutEntry("Rest", "Other", 0, 0, False)]),
    0
)

assert_equal(count_by_category([], "Cardio"), 0)
assert_equal(
    count_by_category(
        [WorkoutEntry("Run", "Cardio", 30, 200, True)],
        "Cardio"
    ),
    1
)
assert_equal(
    count_by_category([
        WorkoutEntry("Run", "Cardio", 30, 200, True),
        WorkoutEntry("Walk", "Cardio", 15, 80, False),
        WorkoutEntry("Lift", "Strength", 45, 300, False)
    ], "Cardio"),
    2
)
assert_equal(
    count_by_category(
        [WorkoutEntry("Run", "Cardio", 30, 200, True)],
        "Strength"
    ),
    0
)

# Navbar test

assert_equal(
    make_navbar(),
    [
        Link("🏡 Home", index),
        Text("  |  "),
        Link("➕ Add Workout", show_add_workout),
        Text("  |  "),
        Link("📙 Log", show_log),
        Text("  |  "),
        Link("📊 Stats", show_stats),
        Text("  |  "),
        Link("🛠️ Settings", show_settings),
        LineBreak(),
        LineBreak()
    ]
)

# Route function tests

test_state = State(
    workouts=[
        WorkoutEntry("Run", "Cardio", 30, 200, True),
        WorkoutEntry("Lift", "Strength", 20, 150, False)
    ],
    daily_goal_minutes=50,
    selected_category="All",
    user_name="Test User",
    fitness_focus="General Health",
    motto="Keep going!"
)

assert_equal(
    index(test_state),
    Page(test_state, [
        *make_navbar(),
        Header("Welcome back, Test User!"),
        Text("Focus Mode: General Health"),
        LineBreak(),
        Text('Motto: "Keep going!"'),
        LineBreak(),
        LineBreak(),
        Header("Today's Progress", level=2),
        Text("• Daily Goal: 50 mins"),
        LineBreak(),
        Text("• Total Logged Today: 50 mins"),
        LineBreak(),
        LineBreak(),
        Text("🎉 Great job! You hit your daily active workout goal!")
    ])
)

empty_state = State(
    [], 50, "All", "Test User", "General Health", "Keep going!"
)

assert_equal(
    index(empty_state),
    Page(empty_state, [
        *make_navbar(),
        Header("Welcome back, Test User!"),
        Text("Focus Mode: General Health"),
        LineBreak(),
        Text('Motto: "Keep going!"'),
        LineBreak(),
        LineBreak(),
        Header("Today's Progress", level=2),
        Text("• Daily Goal: 50 mins"),
        LineBreak(),
        Text("• Total Logged Today: 0 mins"),
        LineBreak(),
        LineBreak(),
        Text("💪 Keep pushing! You need 50 more minutes to reach your goal.")
    ])
)

zero_goal_state = State(
    [], 0, "All", "Test User", "General Health", "Keep going!"
)
assert_equal(
    index(zero_goal_state),
    Page(zero_goal_state, [
        *make_navbar(),
        Header("Welcome back, Test User!"),
        Text("Focus Mode: General Health"),
        LineBreak(),
        Text('Motto: "Keep going!"'),
        LineBreak(),
        LineBreak(),
        Header("Today's Progress", level=2),
        Text("• Daily Goal: 0 mins"),
        LineBreak(),
        Text("• Total Logged Today: 0 mins"),
        LineBreak(),
        LineBreak(),
        Text("🎉 Great job! You hit your daily active workout goal!")
    ])
)

assert_equal(
    show_add_workout(test_state),
    Page(test_state, [
        *make_navbar(),
        Header("Log a New Workout"),
        Text("Exercise Name:"),
        LineBreak(),
        TextBox("name", "Treadmill Run"),
        LineBreak(),
        LineBreak(),
        Text("Category:"),
        LineBreak(),
        SelectBox(
            "category",
            ["Cardio", "Strength", "Flexibility", "Other"]
        ),
        LineBreak(),
        LineBreak(),
        Text("Duration (minutes):"),
        LineBreak(),
        TextBox("duration", "30"),
        LineBreak(),
        LineBreak(),
        Text("Calories Burned:"),
        LineBreak(),
        TextBox("calories", "200"),
        LineBreak(),
        LineBreak(),
        Text("Mark as Favorite Workout:"),
        CheckBox("is_favorite", False),
        LineBreak(),
        LineBreak(),
        Button("Save Workout Session", add_workout_submit)
    ])
)

add_state = State(
    workouts=[
        WorkoutEntry("Run", "Cardio", 30, 200, True),
        WorkoutEntry("Lift", "Strength", 20, 150, False)
    ],
    daily_goal_minutes=50,
    selected_category="All",
    user_name="Test User",
    fitness_focus="General Health",
    motto="Keep going!"
)
assert_equal(
    add_workout_submit(
        add_state, "Swim", "Cardio", "40", "300", True
    ),
    index(add_state)
)
assert_equal(
    add_state.workouts[-1],
    WorkoutEntry("Swim", "Cardio", 40, 300, True)
)

invalid_duration_state = State(
    [], 50, "All", "Test User", "General Health", "Keep going!"
)
assert_equal(
    add_workout_submit(
        invalid_duration_state, "Run", "Cardio", "0", "200", False
    ),
    Page(invalid_duration_state, [
        *make_navbar(),
        Header("Input Error"),
        Text(
            "⚠️ Duration must be greater than 0 and "
            "calories cannot be negative."
        ),
        LineBreak(),
        LineBreak(),
        Link("Go Back & Correct", show_add_workout)
    ])
)
assert_equal(invalid_duration_state.workouts, [])

negative_duration_state = State(
    [], 50, "All", "Test User", "General Health", "Keep going!"
)
assert_equal(
    add_workout_submit(
        negative_duration_state, "Run", "Cardio", "-10", "200", False
    ),
    Page(negative_duration_state, [
        *make_navbar(),
        Header("Input Error"),
        Text(
            "⚠️ Duration must be greater than 0 and "
            "calories cannot be negative."
        ),
        LineBreak(),
        LineBreak(),
        Link("Go Back & Correct", show_add_workout)
    ])
)
assert_equal(negative_duration_state.workouts, [])

negative_calories_state = State(
    [], 50, "All", "Test User", "General Health", "Keep going!"
)
assert_equal(
    add_workout_submit(
        negative_calories_state, "Run", "Cardio", "30", "-1", False
    ),
    Page(negative_calories_state, [
        *make_navbar(),
        Header("Input Error"),
        Text(
            "⚠️ Duration must be greater than 0 and "
            "calories cannot be negative."
        ),
        LineBreak(),
        LineBreak(),
        Link("Go Back & Correct", show_add_workout)
    ])
)
assert_equal(negative_calories_state.workouts, [])

zero_calories_state = State(
    [], 50, "All", "Test User", "General Health", "Keep going!"
)
assert_equal(
    add_workout_submit(
        zero_calories_state, "Run", "Cardio", "30", "0", False
    ),
    index(zero_calories_state)
)
assert_equal(
    zero_calories_state.workouts,
    [WorkoutEntry("Run", "Cardio", 30, 0, False)]
)

empty_log_state = State(
    [], 50, "All", "Test User", "General Health", "Keep going!"
)
assert_equal(
    show_log(empty_log_state),
    Page(empty_log_state, [
        *make_navbar(),
        Header("Workout Log"),
        Text("Filter by Category (Current: All):"),
        LineBreak(),
        SelectBox(
            "category_filter",
            ["All", "Cardio", "Strength", "Flexibility", "Other"]
        ),
        Button("Apply Filter", filter_category),
        LineBreak(),
        LineBreak(),
        Header("Your Logged Activities", level=2),
        Text("No workout records match this category."),
        LineBreak()
    ])
)

assert_equal(
    show_log(test_state),
    Page(test_state, [
        *make_navbar(),
        Header("Workout Log"),
        Text("Filter by Category (Current: All):"),
        LineBreak(),
        SelectBox(
            "category_filter",
            ["All", "Cardio", "Strength", "Flexibility", "Other"]
        ),
        Button("Apply Filter", filter_category),
        LineBreak(),
        LineBreak(),
        Header("Your Logged Activities", level=2),
        Text("• Run (Cardio) — 30 mins | 200 cal ⭐"),
        LineBreak(),
        Text("• Lift (Strength) — 20 mins | 150 cal"),
        LineBreak()
    ])
)

cardio_state = State(
    test_state.workouts,
    50,
    "Cardio",
    "Test User",
    "General Health",
    "Keep going!"
)
assert_equal(
    show_log(cardio_state),
    Page(cardio_state, [
        *make_navbar(),
        Header("Workout Log"),
        Text("Filter by Category (Current: Cardio):"),
        LineBreak(),
        SelectBox(
            "category_filter",
            ["All", "Cardio", "Strength", "Flexibility", "Other"]
        ),
        Button("Apply Filter", filter_category),
        LineBreak(),
        LineBreak(),
        Header("Your Logged Activities", level=2),
        Text("• Run (Cardio) — 30 mins | 200 cal ⭐"),
        LineBreak()
    ])
)

filter_state = State(
    test_state.workouts,
    50,
    "All",
    "Test User",
    "General Health",
    "Keep going!"
)
assert_equal(
    filter_category(filter_state, "Strength"),
    show_log(filter_state)
)
assert_equal(filter_state.selected_category, "Strength")

assert_equal(
    filter_category(empty_log_state, "Cardio"),
    show_log(empty_log_state)
)
assert_equal(empty_log_state.selected_category, "Cardio")

assert_equal(
    show_stats(test_state),
    Page(test_state, [
        *make_navbar(),
        Header("Fitness Summary & Stats"),
        Header("Overview Metrics", level=2),
        Text("• Total Recorded Sessions: 2"),
        LineBreak(),
        Text("• Total Time Exercising: 50 minutes"),
        LineBreak(),
        Text("• Total Energy Burned: 350 cal"),
        LineBreak(),
        Text("• Average Session Duration: 25 minutes/session"),
        LineBreak(),
        LineBreak(),
        Header("Category Breakdown", level=2),
        Text("• Cardio Sessions: 1"),
        LineBreak(),
        Text("• Strength Sessions: 1"),
        LineBreak(),
        Text("• Flexibility Sessions: 0")
    ])
)

assert_equal(
    show_stats(empty_log_state),
    Page(empty_log_state, [
        *make_navbar(),
        Header("Fitness Summary & Stats"),
        Header("Overview Metrics", level=2),
        Text("• Total Recorded Sessions: 0"),
        LineBreak(),
        Text("• Total Time Exercising: 0 minutes"),
        LineBreak(),
        Text("• Total Energy Burned: 0 cal"),
        LineBreak(),
        Text("• Average Session Duration: 0 minutes/session"),
        LineBreak(),
        LineBreak(),
        Header("Category Breakdown", level=2),
        Text("• Cardio Sessions: 0"),
        LineBreak(),
        Text("• Strength Sessions: 0"),
        LineBreak(),
        Text("• Flexibility Sessions: 0")
    ])
)

assert_equal(
    show_settings(test_state),
    Page(test_state, [
        *make_navbar(),
        Header("User Profile & Preferences"),
        Text("Your Name:"),
        LineBreak(),
        TextBox("user_name", "Test User"),
        LineBreak(),
        LineBreak(),
        Text("Primary Fitness Focus:"),
        LineBreak(),
        SelectBox(
            "fitness_focus",
            ["General Health", "Weight Loss", "Muscle Building", "Endurance"]
        ),
        LineBreak(),
        LineBreak(),
        Text("Motivational Motto / Goal Quote:"),
        LineBreak(),
        TextBox("motto", "Keep going!"),
        LineBreak(),
        LineBreak(),
        Text("Daily Target Goal (Minutes):"),
        LineBreak(),
        TextBox("daily_goal", "50"),
        LineBreak(),
        LineBreak(),
        Button("Save Profile & Settings", update_settings)
    ])
)

assert_equal(
    update_settings(
        test_state, "New Name", "Endurance", "Never give up!", "60"
    ),
    index(test_state)
)
assert_equal(test_state.user_name, "New Name")
assert_equal(test_state.fitness_focus, "Endurance")
assert_equal(test_state.motto, "Never give up!")
assert_equal(test_state.daily_goal_minutes, 60)

zero_goal_settings_state = State(
    [], 50, "All", "Test User", "General Health", "Keep going!"
)
assert_equal(
    update_settings(
        zero_goal_settings_state,
        "Test User",
        "General Health",
        "Keep going!",
        "0"
    ),
    index(zero_goal_settings_state)
)
assert_equal(zero_goal_settings_state.daily_goal_minutes, 0)


# Drafter server initialization + template to start the app with some preloaded stuff
initial_state = State(
    workouts=[
        WorkoutEntry("Morning Jog", "Cardio", 25, 180, True),
        WorkoutEntry("Pushups & Core", "Strength", 15, 90, False)
    ],
    daily_goal_minutes=45,
    selected_category="All",
    user_name="Ryan",
    fitness_focus="Weight Loss",
    motto="Consistency over perfection!"
)

start_server(initial_state)
