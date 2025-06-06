import React, { useState, useEffect } from 'react';
import { useAnalytics } from '../../contexts/AnalyticsContext';
import { Row, Col, Select, Spin, Alert, Tabs, DatePicker, Table, Progress, Divider } from 'antd';
import { 
  PieChartOutlined, 
  BarChartOutlined,
  FileTextOutlined,
  ApartmentOutlined
} from '@ant-design/icons';
import ResponsiveCard from '../common/ResponsiveCard';
import ResponsiveTable from '../common/ResponsiveTable';
import { useMediaQuery } from 'react-responsive';
import './TreeOperationsAnalysis.css';

const { TabPane } = Tabs;
const { RangePicker } = DatePicker;
const { Option } = Select;

const TreeOperationsAnalysis = () => {
  const { 
    treeOperationsData, 
    loading, 
    error, 
    fetchTreeOperationsData 
  } = useAnalytics();
  
  const [timeRange, setTimeRange] = useState("month");
  // const isMobile = useMediaQuery({ maxWidth: 576 });
  
  useEffect(() => {
    fetchTreeOperationsData();
  }, [fetchTreeOperationsData]);
  
  const handleTimeRangeChange = (value) => {
    setTimeRange(value);
    // In a real implementation, this would refetch data with the new time range
    fetchTreeOperationsData();
  };
  
  if (loading) {
    return (
      <div className="tree-operations-loading">
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
  
  if (!treeOperationsData || !treeOperationsData.species || !treeOperationsData.operations) {
    return (
      <Alert
        message="No Data"
        description="No tree operations data available."
        type="info"
        showIcon
      />
    );
  }
  
  // Columns for the tree species table
  const speciesColumns = [
    {
      title: 'Tree Species',
      dataIndex: 'species',
      key: 'species',
      sorter: (a, b) => a.species.localeCompare(b.species)
    },
    {
      title: 'Count',
      dataIndex: 'count',
      key: 'count',
      sorter: (a, b) => a.count - b.count
    },
    {
      title: 'Percentage',
      dataIndex: 'percentage',
      key: 'percentage',
      render: (text) => `${text}%`,
      sorter: (a, b) => a.percentage - b.percentage
    },
    {
      title: 'Average Cost',
      dataIndex: 'avg_cost',
      key: 'avg_cost',
      render: (text) => `$${text.toLocaleString()}`,
      sorter: (a, b) => a.avg_cost - b.avg_cost
    },
    {
      title: 'Total Revenue',
      dataIndex: 'total_revenue',
      key: 'total_revenue',
      render: (text) => `$${text.toLocaleString()}`,
      sorter: (a, b) => a.total_revenue - b.total_revenue,
      responsive: 'desktop-only'
    }
  ];
  
  // Columns for the operations table
  const operationsColumns = [
    {
      title: 'Operation Type',
      dataIndex: 'operation',
      key: 'operation',
      sorter: (a, b) => a.operation.localeCompare(b.operation)
    },
    {
      title: 'Count',
      dataIndex: 'count',
      key: 'count',
      sorter: (a, b) => a.count - b.count
    },
    {
      title: 'Percentage',
      dataIndex: 'percentage',
      key: 'percentage',
      render: (text) => `${text}%`,
      sorter: (a, b) => a.percentage - b.percentage
    },
    {
      title: 'Average Cost',
      dataIndex: 'avg_cost',
      key: 'avg_cost',
      render: (text) => `$${text.toLocaleString()}`,
      sorter: (a, b) => a.avg_cost - b.avg_cost
    },
    {
      title: 'Total Revenue',
      dataIndex: 'total_revenue',
      key: 'total_revenue',
      render: (text) => `$${text.toLocaleString()}`,
      sorter: (a, b) => a.total_revenue - b.total_revenue,
      responsive: 'desktop-only'
    }
  ];
  
  // Get top 5 species by count
  const topSpecies = [...treeOperationsData.species]
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);
  
  // Get top 5 operations by count
  const topOperations = [...treeOperationsData.operations]
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);
  
  return (
    <div className="tree-operations-analysis">
      <div className="tree-operations-header">
        <h2>Tree Operations Analysis</h2>
        <div className="tree-operations-controls">
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
      
      <Row gutter={[16, 16]} className="tree-operations-overview">
        <Col xs={24} lg={12}>
          <ResponsiveCard
            title="Tree Species Distribution"
            icon={<PieChartOutlined />}
            className="chart-card"
          >
            <div className="chart-placeholder">
              <div className="chart-placeholder-text">
                <PieChartOutlined />
                <p>Tree Species Distribution Chart</p>
                <p className="chart-placeholder-note">
                  In a real implementation, this would be a pie chart showing the distribution of tree species.
                </p>
              </div>
            </div>
            
            <Divider>Top 5 Tree Species</Divider>
            
            <div className="top-items">
              {topSpecies.map((species, index) => (
                <div key={species.species} className="top-item">
                  <div className="top-item-rank">{index + 1}</div>
                  <div className="top-item-details">
                    <div className="top-item-name">{species.species}</div>
                    <Progress 
                      percent={species.percentage} 
                      size="small" 
                      showInfo={false}
                    />
                  </div>
                  <div className="top-item-stats">
                    <div className="top-item-count">{species.count}</div>
                    <div className="top-item-percentage">{species.percentage}%</div>
                  </div>
                </div>
              ))}
            </div>
          </ResponsiveCard>
        </Col>
        
        <Col xs={24} lg={12}>
          <ResponsiveCard
            title="Operation Types Distribution"
            icon={<PieChartOutlined />}
            className="chart-card"
          >
            <div className="chart-placeholder">
              <div className="chart-placeholder-text">
                <PieChartOutlined />
                <p>Operation Types Distribution Chart</p>
                <p className="chart-placeholder-note">
                  In a real implementation, this would be a pie chart showing the distribution of operation types.
                </p>
              </div>
            </div>
            
            <Divider>Top 5 Operation Types</Divider>
            
            <div className="top-items">
              {topOperations.map((operation, index) => (
                <div key={operation.operation} className="top-item">
                  <div className="top-item-rank">{index + 1}</div>
                  <div className="top-item-details">
                    <div className="top-item-name">{operation.operation}</div>
                    <Progress 
                      percent={operation.percentage} 
                      size="small" 
                      showInfo={false}
                    />
                  </div>
                  <div className="top-item-stats">
                    <div className="top-item-count">{operation.count}</div>
                    <div className="top-item-percentage">{operation.percentage}%</div>
                  </div>
                </div>
              ))}
            </div>
          </ResponsiveCard>
        </Col>
      </Row>
      
      <Row gutter={[16, 16]} className="tree-operations-details">
        <Col xs={24}>
          <Tabs defaultActiveKey="species" className="tree-operations-tabs">
            <TabPane tab="Tree Species Analysis" key="species">
              <ResponsiveCard
                title="Tree Species Details"
                icon={<ApartmentOutlined />}
                className="table-card"
              >
                <ResponsiveTable
                  columns={speciesColumns}
                  dataSource={treeOperationsData.species}
                  rowKey="species"
                  pagination={{ pageSize: 10 }}
                  searchable
                  searchPlaceholder="Search tree species"
                />
              </ResponsiveCard>
            </TabPane>
            
            <TabPane tab="Operation Types Analysis" key="operations">
              <ResponsiveCard
                title="Operation Types Details"
                icon={<FileTextOutlined />}
                className="table-card"
              >
                <ResponsiveTable
                  columns={operationsColumns}
                  dataSource={treeOperationsData.operations}
                  rowKey="operation"
                  pagination={{ pageSize: 10 }}
                  searchable
                  searchPlaceholder="Search operation types"
                />
              </ResponsiveCard>
            </TabPane>
          </Tabs>
        </Col>
      </Row>
      
      <Row gutter={[16, 16]} className="tree-operations-trends">
        <Col xs={24}>
          <ResponsiveCard
            title="Tree Operations Trends"
            icon={<BarChartOutlined />}
            className="chart-card"
          >
            <Tabs defaultActiveKey="species_trend">
              <TabPane tab="Species Trends" key="species_trend">
                <div className="chart-placeholder">
                  <div className="chart-placeholder-text">
                    <BarChartOutlined />
                    <p>Tree Species Trends Chart</p>
                    <p className="chart-placeholder-note">
                      In a real implementation, this would be a line chart showing trends for top tree species over time.
                    </p>
                  </div>
                </div>
              </TabPane>
              <TabPane tab="Operation Trends" key="operation_trend">
                <div className="chart-placeholder">
                  <div className="chart-placeholder-text">
                    <BarChartOutlined />
                    <p>Operation Types Trends Chart</p>
                    <p className="chart-placeholder-note">
                      In a real implementation, this would be a line chart showing trends for top operation types over time.
                    </p>
                  </div>
                </div>
              </TabPane>
              <TabPane tab="Revenue Trends" key="revenue_trend">
                <div className="chart-placeholder">
                  <div className="chart-placeholder-text">
                    <BarChartOutlined />
                    <p>Revenue Trends by Tree Operation</p>
                    <p className="chart-placeholder-note">
                      In a real implementation, this would be a line chart showing revenue trends by tree operation over time.
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

export default TreeOperationsAnalysis;
