import React, { useState, useEffect } from 'react';
import { useAnalytics } from '../../contexts/AnalyticsContext';
import { Row, Col, Select, Spin, Alert, Tabs, Progress } from 'antd';
import { 
  BarChartOutlined, 
  TeamOutlined,
  UserOutlined,
  TrophyOutlined,
  PercentageOutlined
} from '@ant-design/icons';
import ResponsiveCard from '../common/ResponsiveCard';
import ResponsiveTable from '../common/ResponsiveTable';
import { useMediaQuery } from 'react-responsive';
import './PartnerPerformance.css';

const { TabPane } = Tabs;
const { Option } = Select;

const PartnerPerformance = () => {
  const { 
    partnerData, 
    loading, 
    error, 
    fetchPartnerData 
  } = useAnalytics();
  
  const [timeRange, setTimeRange] = useState("month");
  // const isMobile = useMediaQuery({ maxWidth: 576 });
  
  useEffect(() => {
    fetchPartnerData();
  }, [fetchPartnerData]);
  
  const handleTimeRangeChange = (value) => {
    setTimeRange(value);
    // In a real implementation, this would refetch data with the new time range
    fetchPartnerData();
  };
  
  if (loading) {
    return (
      <div className="partner-performance-loading">
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
  
  if (!partnerData || partnerData.length === 0) {
    return (
      <Alert
        message="No Data"
        description="No partner performance data available."
        type="info"
        showIcon
      />
    );
  }
  
  // Columns for the partner performance table
  const columns = [
    {
      title: 'Partner',
      dataIndex: 'partner_name',
      key: 'partner_name',
      render: (text) => (
        <span>
          <UserOutlined /> {text}
        </span>
      ),
      sorter: (a, b) => a.partner_name.localeCompare(b.partner_name)
    },
    {
      title: 'Region',
      dataIndex: 'region',
      key: 'region',
      sorter: (a, b) => a.region.localeCompare(b.region),
      responsive: 'desktop-only'
    },
    {
      title: 'Leads Assigned',
      dataIndex: 'leads_assigned',
      key: 'leads_assigned',
      sorter: (a, b) => a.leads_assigned - b.leads_assigned
    },
    {
      title: 'Quotes Created',
      dataIndex: 'quotes_created',
      key: 'quotes_created',
      sorter: (a, b) => a.quotes_created - b.quotes_created
    },
    {
      title: 'Conversion Rate',
      dataIndex: 'conversion_rate',
      key: 'conversion_rate',
      render: (text) => `${text}%`,
      sorter: (a, b) => a.conversion_rate - b.conversion_rate
    },
    {
      title: 'Revenue',
      dataIndex: 'revenue',
      key: 'revenue',
      render: (text) => `$${text.toLocaleString()}`,
      sorter: (a, b) => a.revenue - b.revenue
    },
    {
      title: 'Performance',
      dataIndex: 'performance',
      key: 'performance',
      render: (performance) => {
        let color = 'success';
        if (performance < 90) {
          color = 'normal';
        }
        if (performance < 70) {
          color = 'exception';
        }
        return (
          <Progress 
            percent={performance} 
            size="small" 
            status={color}
            format={(percent) => `${percent}%`}
          />
        );
      },
      sorter: (a, b) => a.performance - b.performance
    }
  ];
  
  // Get top 3 partners by performance
  const topPartners = [...partnerData]
    .sort((a, b) => b.performance - a.performance)
    .slice(0, 3);
  
  return (
    <div className="partner-performance">
      <div className="partner-performance-header">
        <h2>Partner Performance</h2>
        <div className="partner-performance-controls">
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
      
      <Row gutter={[16, 16]} className="partner-performance-top">
        <Col xs={24} md={8}>
          <ResponsiveCard
            title="Top Performer"
            icon={<TrophyOutlined style={{ color: '#FFD700' }} />}
            className="top-partner-card gold"
          >
            {topPartners.length > 0 && (
              <div className="top-partner">
                <div className="top-partner-name">
                  <UserOutlined /> {topPartners[0].partner_name}
                </div>
                <div className="top-partner-region">
                  Region: {topPartners[0].region}
                </div>
                <div className="top-partner-stats">
                  <div className="top-partner-stat">
                    <div className="stat-label">Conversion Rate</div>
                    <div className="stat-value">{topPartners[0].conversion_rate}%</div>
                  </div>
                  <div className="top-partner-stat">
                    <div className="stat-label">Revenue</div>
                    <div className="stat-value">${topPartners[0].revenue.toLocaleString()}</div>
                  </div>
                </div>
                <div className="top-partner-performance">
                  <Progress 
                    percent={topPartners[0].performance} 
                    status="success"
                    format={(percent) => `${percent}%`}
                  />
                </div>
              </div>
            )}
          </ResponsiveCard>
        </Col>
        
        <Col xs={24} md={8}>
          <ResponsiveCard
            title="Second Place"
            icon={<TrophyOutlined style={{ color: '#C0C0C0' }} />}
            className="top-partner-card silver"
          >
            {topPartners.length > 1 && (
              <div className="top-partner">
                <div className="top-partner-name">
                  <UserOutlined /> {topPartners[1].partner_name}
                </div>
                <div className="top-partner-region">
                  Region: {topPartners[1].region}
                </div>
                <div className="top-partner-stats">
                  <div className="top-partner-stat">
                    <div className="stat-label">Conversion Rate</div>
                    <div className="stat-value">{topPartners[1].conversion_rate}%</div>
                  </div>
                  <div className="top-partner-stat">
                    <div className="stat-label">Revenue</div>
                    <div className="stat-value">${topPartners[1].revenue.toLocaleString()}</div>
                  </div>
                </div>
                <div className="top-partner-performance">
                  <Progress 
                    percent={topPartners[1].performance} 
                    status="success"
                    format={(percent) => `${percent}%`}
                  />
                </div>
              </div>
            )}
          </ResponsiveCard>
        </Col>
        
        <Col xs={24} md={8}>
          <ResponsiveCard
            title="Third Place"
            icon={<TrophyOutlined style={{ color: '#CD7F32' }} />}
            className="top-partner-card bronze"
          >
            {topPartners.length > 2 && (
              <div className="top-partner">
                <div className="top-partner-name">
                  <UserOutlined /> {topPartners[2].partner_name}
                </div>
                <div className="top-partner-region">
                  Region: {topPartners[2].region}
                </div>
                <div className="top-partner-stats">
                  <div className="top-partner-stat">
                    <div className="stat-label">Conversion Rate</div>
                    <div className="stat-value">{topPartners[2].conversion_rate}%</div>
                  </div>
                  <div className="top-partner-stat">
                    <div className="stat-label">Revenue</div>
                    <div className="stat-value">${topPartners[2].revenue.toLocaleString()}</div>
                  </div>
                </div>
                <div className="top-partner-performance">
                  <Progress 
                    percent={topPartners[2].performance} 
                    status="success"
                    format={(percent) => `${percent}%`}
                  />
                </div>
              </div>
            )}
          </ResponsiveCard>
        </Col>
      </Row>
      
      <Row gutter={[16, 16]} className="partner-performance-overview">
        <Col xs={24}>
          <ResponsiveCard
            title="Partner Performance Comparison"
            icon={<BarChartOutlined />}
            className="chart-card"
          >
            <div className="chart-placeholder">
              <div className="chart-placeholder-text">
                <BarChartOutlined />
                <p>Partner Performance Chart</p>
                <p className="chart-placeholder-note">
                  In a real implementation, this would be a bar chart comparing performance metrics across partners.
                </p>
              </div>
            </div>
          </ResponsiveCard>
        </Col>
      </Row>
      
      <Row gutter={[16, 16]} className="partner-performance-details">
        <Col xs={24}>
          <ResponsiveCard
            title="Partner Performance Metrics"
            icon={<TeamOutlined />}
            className="table-card"
          >
            <ResponsiveTable
              columns={columns}
              dataSource={partnerData}
              rowKey="partner_id"
              pagination={{ pageSize: 5 }}
              searchable
              searchPlaceholder="Search partners"
              filterable
              filterOptions={[
                { label: 'High Performance (>90%)', value: 'high' },
                { label: 'Medium Performance (70-90%)', value: 'medium' },
                { label: 'Low Performance (<70%)', value: 'low' }
              ]}
            />
          </ResponsiveCard>
        </Col>
      </Row>
      
      <Row gutter={[16, 16]} className="partner-performance-trends">
        <Col xs={24}>
          <ResponsiveCard
            title="Partner Trends"
            icon={<BarChartOutlined />}
            className="chart-card"
          >
            <Tabs defaultActiveKey="conversion">
              <TabPane tab="Conversion Rate" key="conversion">
                <div className="chart-placeholder">
                  <div className="chart-placeholder-text">
                    <PercentageOutlined />
                    <p>Partner Conversion Rate Trends</p>
                    <p className="chart-placeholder-note">
                      In a real implementation, this would be a line chart showing conversion rate trends for top partners.
                    </p>
                  </div>
                </div>
              </TabPane>
              <TabPane tab="Revenue" key="revenue">
                <div className="chart-placeholder">
                  <div className="chart-placeholder-text">
                    <BarChartOutlined />
                    <p>Partner Revenue Trends</p>
                    <p className="chart-placeholder-note">
                      In a real implementation, this would be a line chart showing revenue trends for top partners.
                    </p>
                  </div>
                </div>
              </TabPane>
              <TabPane tab="Lead Volume" key="leads">
                <div className="chart-placeholder">
                  <div className="chart-placeholder-text">
                    <BarChartOutlined />
                    <p>Partner Lead Volume Trends</p>
                    <p className="chart-placeholder-note">
                      In a real implementation, this would be a line chart showing lead volume trends for top partners.
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

export default PartnerPerformance;
