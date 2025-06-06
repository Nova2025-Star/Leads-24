import React from 'react';
import { useMediaQuery } from 'react-responsive';
import { Card, Row, Col, Typography, Button } from 'antd';
import './ResponsiveCard.css';

const { Title } = Typography;

const ResponsiveCard = ({ 
  title, 
  icon, 
  children, 
  actions = [], 
  loading = false,
  className = '',
  headerExtra = null
}) => {
  // Media queries for responsive design
  const isMobile = useMediaQuery({ maxWidth: 576 });
  const isTablet = useMediaQuery({ minWidth: 577, maxWidth: 992 });
  
  return (
    <Card
      className={`responsive-card ${className} ${isMobile ? 'mobile' : ''} ${isTablet ? 'tablet' : ''}`}
      loading={loading}
      title={
        <div className="responsive-card-header">
          {icon && <span className="responsive-card-icon">{icon}</span>}
          <Title level={isMobile ? 5 : 4} className="responsive-card-title">
            {title}
          </Title>
          {headerExtra && (
            <div className="responsive-card-extra">
              {headerExtra}
            </div>
          )}
        </div>
      }
      actions={actions.length > 0 ? actions.map((action, index) => (
        <Button 
          key={index}
          type={action.type || "default"}
          icon={action.icon}
          onClick={action.onClick}
          size={isMobile ? "small" : "middle"}
        >
          {!isMobile && action.text}
        </Button>
      )) : undefined}
    >
      <div className="responsive-card-content">
        {children}
      </div>
    </Card>
  );
};

export const ResponsiveCardGrid = ({ children, gutter = [16, 16] }) => {
  // Media queries for responsive design
  const isMobile = useMediaQuery({ maxWidth: 576 });
  const isTablet = useMediaQuery({ minWidth: 577, maxWidth: 992 });
  
  // Determine column spans based on screen size
  const getColSpan = (colSpan) => {
    if (isMobile) {
      return 24; // Full width on mobile
    } else if (isTablet) {
      return colSpan <= 12 ? 12 : 24; // Half width or full width on tablet
    } else {
      return colSpan; // Original span on desktop
    }
  };
  
  return (
    <Row gutter={gutter} className="responsive-card-grid">
      {React.Children.map(children, child => {
        // If the child is a Col component, adjust its span
        if (React.isValidElement(child) && child.type === Col) {
          return React.cloneElement(child, {
            ...child.props,
            span: getColSpan(child.props.span)
          });
        }
        // Otherwise, wrap it in a Col with appropriate span
        return (
          <Col span={getColSpan(24)}>
            {child}
          </Col>
        );
      })}
    </Row>
  );
};

export default ResponsiveCard;
