import React, { useState, useEffect } from "react";
import { useAnalytics } from "../../contexts/AnalyticsContext";
import { Row, Col, Select, Spin, Alert, Tabs, Tag } from 'antd';
import { 
  BarChartOutlined, 
  TeamOutlined,
  GlobalOutlined,
  EnvironmentOutlined
} from '@ant-design/icons';
import ResponsiveCard from '../common/ResponsiveCard';
import ResponsiveTable from '../common/ResponsiveTable';
import { useMediaQuery } from 'react-responsive';
import './RegionalAnalysis.css';

const { TabPane } = Tabs;

const { Option } = Select;

const RegionalAnalysis = () => {
  const { 
    regionalData, 
    loading, 
    error, 
    fetchRegionalData 
  } = useAnalytics();
  
  const [selectedRegion, setSelectedRegion] = useState("all");
  // const isMobile = useMediaQuery({ maxWidth: 576 });
  
  useEffect(() => {
    fetchRegionalData();
  }, [fetchRegionalData]);
  
  const handleRegionChange = (value) => {
    setSelectedRegion(value);
    // In a real implementation, this would refetch data for the specific region
  };
  
  if (loading) {
    return (
      <div className="regional-analysis-loading">
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
  
  if (!regionalData || regionalData.length === 0) {
    return (
      <Alert
        message="No Data"
        description="No regional data available."
        type="info"
        showIcon
      />
    );
  }
  
  // Columns for the regional performance table
  const columns = [
    {
      title: 'Region',
      dataIndex: 'region',
      key: 'region',
      render: (text) => (
        <span>
          <EnvironmentOutlined /> {text}
        </span>
      ),
      sorter: (a, b) => a.region.localeCompare(b.region)
    },
    {
      title: 'Total Leads',
      dataIndex: 'total_leads',
      key: 'total_leads',
      sorter: (a, b) => a.total_leads - b.total_leads
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
      title: 'Avg. Quote Value',
      dataIndex: 'avg_quote_value',
      key: 'avg_quote_value',
      render: (text) => `$${text.toLocaleString()}`,
      sorter: (a, b) => a.avg_quote_value - b.avg_quote_value,
      responsive: 'desktop-only'
    },
    {
      title: 'Performance',
      dataIndex: 'performance',
      key: 'performance',
      render: (performance) => {
        let color = 'green';
        if (performance < 90) {
          color = 'orange';
        }
        if (performance < 70) {
          color = 'red';
        }
        return (
          <Tag color={color}>
            {performance}%
          </Tag>
        );
      },
      sorter: (a, b) => a.performance - b.performance
    }
  ];
  
  return (
    <div className="regional-analysis">
      <div className="regional-analysis-header">
        <h2>Regional Analysis</h2>
        <div className="regional-analysis-controls">
          <Select 
            defaultValue="all" 
            style={{ width: 150 }} 
            onChange={handleRegionChange}
            value={selectedRegion}
          >
            <Option value="all">All Regions</Option>
            {regionalData.map(region => (
              <Option key={region.region} value={region.region}>
                {region.region}
              </Option>
            ))}
          </Select>
        </div>
      </div>
      
      <Row gutter={[16, 16]} className="regional-analysis-overview">
        <Col xs={24}>
          <ResponsiveCard
            title="Regional Performance Comparison"
            icon={<GlobalOutlined />}
            className="chart-card"
          >
            <div className="chart-placeholder">
              <div className="chart-placeholder-text">
                <BarChartOutlined />
                <p>Regional Performance Chart</p>
                <p className="chart-placeholder-note">
                  In a real implementation, this would be a bar chart comparing performance metrics across regions.
                </p>
              </div>
            </div>
          </ResponsiveCard>
        </Col>
      </Row>
      
      <Row gutter={[16, 16]} className="regional-analysis-details">
        <Col xs={24}>
          <ResponsiveCard
            title="Regional Performance Metrics"
            icon={<TeamOutlined />}
            className="table-card"
          >
            <ResponsiveTable
              columns={columns}
              dataSource={regionalData}
              rowKey="region"
              pagination={{ pageSize: 5 }}
              searchable
              searchPlaceholder="Search regions"
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
      
      <Row gutter={[16, 16]} className="regional-analysis-trends">
        <Col xs={24}>
          <ResponsiveCard
            title="Regional Trends"
            icon={<BarChartOutlined />}
            className="chart-card"
          >
            <Tabs defaultActiveKey="leads">
              <TabPane tab="Leads by Region" key="leads">
                <div className="chart-placeholder">
                  <div className="chart-placeholder-text">
                    <BarChartOutlined />
                    <p>Leads by Region Chart</p>
                    <p className="chart-placeholder-note">
                      In a real implementation, this would be a chart showing lead distribution by region over time.
                    </p>
                  </div>
                </div>
              </TabPane>
              <TabPane tab="Conversion by Region" key="conversion">
                <div className="chart-placeholder">
                  <div className="chart-placeholder-text">
                    <BarChartOutlined />
                    <p>Conversion by Region Chart</p>
                    <p className="chart-placeholder-note">
                      In a real implementation, this would be a chart showing conversion rates by region over time.
                    </p>
                  </div>
                </div>
              </TabPane>
              <TabPane tab="Revenue by Region" key="revenue">
                <div className="chart-placeholder">
                  <div className="chart-placeholder-text">
                    <BarChartOutlined />
                    <p>Revenue by Region Chart</p>
                    <p className="chart-placeholder-note">
                      In a real implementation, this would be a chart showing revenue by region over time.
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

export default RegionalAnalysis;
