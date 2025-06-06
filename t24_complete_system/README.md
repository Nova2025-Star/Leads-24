# T24 Arborist Lead System

This is a comprehensive lead management system for arborist service companies, featuring both backend and frontend components with enhanced functionality.

## System Overview

The T24 Arborist Lead System streamlines the entire lead management lifecycle, from initial customer inquiry to job completion and payment processing. It facilitates efficient communication between administrators, franchise partners, and customers while providing robust analytics and financial tracking capabilities.

## Features

### Core Features
- Lead management and assignment
- Quote creation and management
- Partner/franchise management
- Customer relationship management
- User authentication and authorization

### Enhanced Features
- Email notification system
- Mobile application integration
- Advanced reporting and analytics
- Customer portal for quote approval
- Integration with accounting systems

## System Requirements

- Docker and Docker Compose
- Internet connection
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Getting Started

1. Extract the zip file to your preferred location
2. Navigate to the extracted directory
3. Run the start script:
   - On Linux/Mac: `./start.sh`
   - On Windows: `start.bat`
4. Access the system at: http://localhost
5. Log in with the default credentials:
   - Admin: admin@t24leads.se / admin123
   - Partner: partner1@t24leads.se / partner1

**Important Note**: The system uses these exact credentials for the sample data. Make sure to enter them exactly as shown above, including the correct email addresses and passwords.

## Directory Structure

```
t24_complete_system/
├── backend/              # Backend API services
│   ├── app/              # Application code
│   │   ├── models/       # Database models
│   │   ├── routes/       # API endpoints
│   │   ├── schemas/      # Data validation schemas
│   │   └── utils/        # Utility functions
│   └── requirements.txt  # Python dependencies
├── frontend/             # Frontend React application
│   ├── public/           # Static assets
│   ├── src/              # Source code
│   │   ├── components/   # React components
│   │   ├── contexts/     # Context providers
│   │   ├── layouts/      # Page layouts
│   │   ├── pages/        # Page components
│   │   └── services/     # API services
│   └── package.json      # Node.js dependencies
├── docs/                 # Documentation
├── docker-compose.yml    # Docker configuration
├── .env                  # Environment variables
├── start.sh              # Linux/Mac startup script
└── start.bat             # Windows startup script
```

## Technology Stack

- **Backend**: FastAPI (Python), PostgreSQL
- **Frontend**: React.js, Ant Design
- **Containerization**: Docker, Docker Compose

## Security Features

- JWT-based authentication
- Bcrypt password hashing
- Role-based access control
- Secure API endpoints

## Troubleshooting

### Authentication Issues
- Ensure you're using the exact credentials as listed above
- The system is case-sensitive for both email addresses and passwords
- If you continue to experience issues, check the backend logs for more details

## Support

For any issues or questions, please contact support@t24leads.se
