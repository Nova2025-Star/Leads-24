import React, { useState, useEffect } from "react";
import { useAnalytics } from "../../contexts/AnalyticsContext";
import { Row, Col, Statistic, Spin, Alert, Tabs, DatePicker, Select } from 'antd';
import { 
  LineChartOutlined, 
  PieChartOutlined, 
  DollarOutlined,
  UserOutlined,
  FileTextOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import ResponsiveCard from '../common/ResponsiveCard';
import { useMediaQuery } from 'react-responsive';
import './PerformanceDashboard.css';

const { TabPane } = Tabs;

const { Option } = Select;

const PerformanceDashboard = () => {
  const { 
    performanceMetrics, 
    loading, 
    error, 
    fetchPerformanceMetrics 
  } = useAnalytics();
  
  const [timeRange, setTimeRange] = useState("month");
  // const isMobile = useMediaQuery({ maxWidth: 576 });
  
  useEffect(() => {
    fetchPerformanceMetrics();
  }, [fetchPerformanceMetrics]);
  
  const handleTimeRangeChange = (value) => {
    setTimeRange(value);
    // In a real implementation, this would refetch data with the new time range
    fetchPerformanceMetrics();
  };
  
  if (loading) {
    return (
      <div className="performance-dashboard-loading">
        <Spin size="large" />
      </div>
    );
  }
  
  if (error) {
    return (
      <Alert
        message="Error"
        description={error}
        type="error"
        showIcon
      />
    );
  }
  
  if (!performanceMetrics) {
    return (
      <Alert
        message="No Data"
        description="No performance metrics available."
        type="info"
        showIcon
      />
    );
  }
  
  return (
    <div className="performance-dashboard">
      <div className="performance-dashboard-header">
        <h2>Performance Dashboard</h2>
        <div className="performance-dashboard-controls">
          <Select 
            defaultValue="month" 
            style={{ width: 120 }} 
            onChange={handleTimeRangeChange}
            value={timeRange}
          >
            <Option value="week">This Week</Option>
            <Option value="month">This Month</Option>
            <Option value="quarter">This Quarter</Option>
            <Option value="year">This Year</Option>
          </Select>
        </div>
      </div>
      
      <Row gutter={[16, 16]} className="performance-dashboard-metrics">
        <Col xs={24} sm={12} lg={6}>
          <ResponsiveCard
            title="Total Leads"
            icon={<UserOutlined />}
            className="metric-card leads"
          >
            <Statistic 
              value={performanceMetrics.total_leads} 
              precision={0} 
            />
            <div className="metric-change">
              {performanceMetrics.lead_growth >= 0 ? (
                <span className="positive">+{performanceMetrics.lead_growth}%</span>
              ) : (
                <span className="negative">{performanceMetrics.lead_growth}%</span>
              )}
              <span className="period">vs. previous {timeRange}</span>
            </div>
          </ResponsiveCard>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <ResponsiveCard
            title="Conversion Rate"
            icon={<CheckCircleOutlined />}
            className="metric-card conversion"
          >
            <Statistic 
              value={performanceMetrics.conversion_rate} 
              precision={1}
              suffix="%" 
            />
            <div className="metric-change">
              {performanceMetrics.conversion_change >= 0 ? (
                <span className="positive">+{performanceMetrics.conversion_change}%</span>
              ) : (
                <span className="negative">{performanceMetrics.conversion_change}%</span>
              )}
              <span className="period">vs. previous {timeRange}</span>
            </div>
          </ResponsiveCard>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <ResponsiveCard
            title="Total Revenue"
            icon={<DollarOutlined />}
            className="metric-card revenue"
          >
            <Statistic 
              value={performanceMetrics.total_revenue} 
              precision={0}
              prefix="$" 
            />
            <div className="metric-change">
              {performanceMetrics.revenue_growth >= 0 ? (
                <span className="positive">+{performanceMetrics.revenue_growth}%</span>
              ) : (
                <span className="negative">{performanceMetrics.revenue_growth}%</span>
              )}
              <span className="period">vs. previous {timeRange}</span>
            </div>
          </ResponsiveCard>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <ResponsiveCard
            title="Average Quote Value"
            icon={<FileTextOutlined />}
            className="metric-card average"
          >
            <Statistic 
              value={performanceMetrics.avg_quote_value} 
              precision={0}
              prefix="$" 
            />
            <div className="metric-change">
              {performanceMetrics.avg_quote_change >= 0 ? (
                <span className="positive">+{performanceMetrics.avg_quote_change}%</span>
              ) : (
                <span className="negative">{performanceMetrics.avg_quote_change}%</span>
              )}
              <span className="period">vs. previous {timeRange}</span>
            </div>
          </ResponsiveCard>
        </Col>
      </Row>
      
      <Row gutter={[16, 16]} className="performance-dashboard-details">
        <Col xs={24} lg={12}>
          <ResponsiveCard
            title="Lead Status Distribution"
            icon={<PieChartOutlined />}
            className="chart-card"
          >
            <div className="chart-placeholder">
              <div className="chart-placeholder-text">
                <PieChartOutlined />
                <p>Lead Status Distribution Chart</p>
                <p className="chart-placeholder-note">
                  In a real implementation, this would be a pie chart showing the distribution of leads by status.
                </p>
              </div>
            </div>
            
            <div className="chart-legend">
              <div className="legend-item">
                <span className="legend-color new"></span>
                <span className="legend-label">New: {performanceMetrics.lead_status.new}</span>
              </div>
              <div className="legend-item">
                <span className="legend-color assigned"></span>
                <span className="legend-label">Assigned: {performanceMetrics.lead_status.assigned}</span>
              </div>
              <div className="legend-item">
                <span className="legend-color quoted"></span>
                <span className="legend-label">Quoted: {performanceMetrics.lead_status.quoted}</span>
              </div>
              <div className="legend-item">
                <span className="legend-color approved"></span>
                <span className="legend-label">Approved: {performanceMetrics.lead_status.approved}</span>
              </div>
              <div className="legend-item">
                <span className="legend-color declined"></span>
                <span className="legend-label">Declined: {performanceMetrics.lead_status.declined}</span>
              </div>
            </div>
          </ResponsiveCard>
        </Col>
        
        <Col xs={24} lg={12}>
          <ResponsiveCard
            title="Quote Status Distribution"
            icon={<PieChartOutlined />}
            className="chart-card"
          >
            <div className="chart-placeholder">
              <div className="chart-placeholder-text">
                <PieChartOutlined />
                <p>Quote Status Distribution Chart</p>
                <p className="chart-placeholder-note">
                  In a real implementation, this would be a pie chart showing the distribution of quotes by status.
                </p>
              </div>
            </div>
            
            <div className="chart-legend">
              <div className="legend-item">
                <span className="legend-color draft"></span>
                <span className="legend-label">Draft: {performanceMetrics.quote_status.draft}</span>
              </div>
              <div className="legend-item">
                <span className="legend-color sent"></span>
                <span className="legend-label">Sent: {performanceMetrics.quote_status.sent}</span>
              </div>
              <div className="legend-item">
                <span className="legend-color approved"></span>
                <span className="legend-label">Approved: {performanceMetrics.quote_status.approved}</span>
              </div>
              <div className="legend-item">
                <span className="legend-color declined"></span>
                <span className="legend-label">Declined: {performanceMetrics.quote_status.declined}</span>
              </div>
              <div className="legend-item">
                <span className="legend-color expired"></span>
                <span className="legend-label">Expired: {performanceMetrics.quote_status.expired}</span>
              </div>
            </div>
          </ResponsiveCard>
        </Col>
      </Row>
      
      <Row gutter={[16, 16]} className="performance-dashboard-trends">
        <Col xs={24}>
          <ResponsiveCard
            title="Performance Trends"
            icon={<LineChartOutlined />}
            className="chart-card"
          >
            <Tabs defaultActiveKey="leads">
              <TabPane tab="Leads" key="leads">
                <div className="chart-placeholder">
                  <div className="chart-placeholder-text">
                    <LineChartOutlined />
                    <p>Lead Trends Chart</p>
                    <p className="chart-placeholder-note">
                      In a real implementation, this would be a line chart showing lead trends over time.
                    </p>
                  </div>
                </div>
              </TabPane>
              <TabPane tab="Conversion" key="conversion">
                <div className="chart-placeholder">
                  <div className="chart-placeholder-text">
                    <LineChartOutlined />
                    <p>Conversion Rate Trends Chart</p>
                    <p className="chart-placeholder-note">
                      In a real implementation, this would be a line chart showing conversion rate trends over time.
                    </p>
                  </div>
                </div>
              </TabPane>
              <TabPane tab="Revenue" key="revenue">
                <div className="chart-placeholder">
                  <div className="chart-placeholder-text">
                    <LineChartOutlined />
                    <p>Revenue Trends Chart</p>
                    <p className="chart-placeholder-note">
                      In a real implementation, this would be a line chart showing revenue trends over time.
                    </p>
                  </div>
                </div>
              </TabPane>
            </Tabs>
          </ResponsiveCard>
        </Col>
      </Row>
    </div>
  );
};

export default PerformanceDashboard;
