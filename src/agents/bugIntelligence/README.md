# BugIntelligence

This project implements an AI agent that interacts with the Bugzilla API using a local Ollama module. The frontend is built with Streamlit, allowing users to easily query and manage bugs.

## Project Structure

```
bugIntelligence
├── app.py                     # Main application file
├── requirements.txt           # Project dependencies
├── README.md                  # Project documentation
└── .gitignore                 # Git ignore file
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/bugIntelligence.git
   cd bugIntelligence
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command:
```
streamlit run app.py
```

Once the application is running, you can interact with the AI agent through the Streamlit interface. Input your queries related to Bugzilla, and the AI agent will process them using the Ollama module.

## Features

- Query bugs from Bugzilla
- Update bug statuses
- Retrieve detailed information about specific bugs
- User-friendly interface for seamless interaction

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
