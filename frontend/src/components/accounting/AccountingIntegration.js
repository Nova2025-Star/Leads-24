import React, { useState, useEffect } from 'react';
import { useAccounting } from '../../contexts/AccountingContext';
import { Card, Row, Col, Button, Spin, Alert, Tabs, List, Tag, Typography, Modal, Form, Input, Select } from 'antd';
import { 
  BankOutlined, 
  LinkOutlined,
  DisconnectOutlined,
  SyncOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LockOutlined,
  UserOutlined
} from '@ant-design/icons';
import ResponsiveCard from '../common/ResponsiveCard';
import ResponsiveForm from '../common/ResponsiveForm';
import { useMediaQuery } from 'react-responsive';
import './AccountingIntegration.css';

const { Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;

const AccountingIntegration = () => {
  const { 
    accountingSystems,
    connectedSystems,
    syncStatus,
    loading,
    error,
    fetchAccountingSystems,
    fetchConnectedSystems,
    connectAccountingSystem,
    disconnectAccountingSystem,
    syncWithAccountingSystem
  } = useAccounting();
  
  const [connectModalVisible, setConnectModalVisible] = useState(false);
  const [selectedSystem, setSelectedSystem] = useState(null);
  const [form] = Form.useForm();
  // const isMobile = useMediaQuery({ maxWidth: 576 });
  
  useEffect(() => {
    fetchAccountingSystems();
    fetchConnectedSystems();
  }, [fetchAccountingSystems, fetchConnectedSystems]);
  
  const showConnectModal = (system) => {
    setSelectedSystem(system);
    setConnectModalVisible(true);
  };
  
  const handleConnect = async (values) => {
    if (!selectedSystem) return;
    
    const result = await connectAccountingSystem(selectedSystem.id, values);
    if (result) {
      setConnectModalVisible(false);
      form.resetFields();
    }
  };
  
  const handleDisconnect = async (connectionId) => {
    Modal.confirm({
      title: 'Disconnect Accounting System',
      content: 'Are you sure you want to disconnect this accounting system? This will remove all integration settings.',
      okText: 'Disconnect',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        await disconnectAccountingSystem(connectionId);
      }
    });
  };
  
  const handleSync = async (connectionId) => {
    await syncWithAccountingSystem(connectionId);
  };
  
  // Get sync status tag
  const getSyncStatusTag = (connectionId) => {
    const status = syncStatus[connectionId];
    
    if (!status) return null;
    
    switch (status) {
      case 'syncing':
        return <Tag icon={<SyncOutlined spin />} color="processing">Syncing</Tag>;
      case 'success':
        return <Tag icon={<CheckCircleOutlined />} color="success">Sync Complete</Tag>;
      case 'error':
        return <Tag icon={<CloseCircleOutlined />} color="error">Sync Failed</Tag>;
      default:
        return null;
    }
  };
  
  if (loading && accountingSystems.length === 0 && connectedSystems.length === 0) {
    return (
      <div className="accounting-integration-loading">
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
  
  return (
    <div className="accounting-integration">
      <Tabs defaultActiveKey="connected" className="accounting-tabs">
        <TabPane 
          tab={
            <span>
              <LinkOutlined /> Connected Systems
              {connectedSystems.length > 0 && (
                <Tag className="tab-count">{connectedSystems.length}</Tag>
              )}
            </span>
          } 
          key="connected"
        >
          <div className="connected-systems">
            {connectedSystems.length === 0 ? (
              <Alert
                message="No Connected Systems"
                description="You haven't connected any accounting systems yet. Connect an accounting system to sync your financial data."
                type="info"
                showIcon
              />
            ) : (
              <List
                dataSource={connectedSystems}
                renderItem={connection => (
                  <List.Item
                    key={connection.id}
                    actions={[
                      <Button
                        icon={<SyncOutlined />}
                        onClick={() => handleSync(connection.id)}
                        loading={syncStatus[connection.id] === 'syncing'}
                      >
                        Sync
                      </Button>,
                      <Button
                        danger
                        icon={<DisconnectOutlined />}
                        onClick={() => handleDisconnect(connection.id)}
                      >
                        Disconnect
                      </Button>
                    ]}
                    className="connected-system-item"
                  >
                    <List.Item.Meta
                      avatar={<BankOutlined className="system-icon" />}
                      title={
                        <div className="system-title">
                          <span>{connection.system_name}</span>
                          {getSyncStatusTag(connection.id)}
                        </div>
                      }
                      description={
                        <div className="system-details">
                          <div className="system-detail">
                            <Text strong>Account:</Text> {connection.account_name}
                          </div>
                          <div className="system-detail">
                            <Text strong>Connected:</Text> {new Date(connection.connected_at).toLocaleDateString()}
                          </div>
                          <div className="system-detail">
                            <Text strong>Last Sync:</Text> {connection.last_sync ? new Date(connection.last_sync).toLocaleString() : 'Never'}
                          </div>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            )}
          </div>
        </TabPane>
        
        <TabPane 
          tab={
            <span>
              <BankOutlined /> Available Systems
              {accountingSystems.length > 0 && (
                <Tag className="tab-count">{accountingSystems.length}</Tag>
              )}
            </span>
          } 
          key="available"
        >
          <div className="available-systems">
            <Row gutter={[16, 16]}>
              {accountingSystems.map(system => (
                <Col xs={24} sm={12} md={8} key={system.id}>
                  <ResponsiveCard
                    title={system.name}
                    icon={<BankOutlined />}
                    className="system-card"
                    actions={[
                      <Button 
                        type="primary" 
                        icon={<LinkOutlined />}
                        onClick={() => showConnectModal(system)}
                      >
                        Connect
                      </Button>
                    ]}
                  >
                    <div className="system-card-content">
                      <Paragraph>{system.description}</Paragraph>
                      <div className="system-features">
                        <Text strong>Features:</Text>
                        <ul>
                          {system.features.map((feature, index) => (
                            <li key={index}>{feature}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </ResponsiveCard>
                </Col>
              ))}
            </Row>
          </div>
        </TabPane>
      </Tabs>
      
      {/* Connect System Modal */}
      <Modal
        title={`Connect to ${selectedSystem?.name || 'Accounting System'}`}
        open={connectModalVisible}
        onCancel={() => setConnectModalVisible(false)}
        footer={null}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleConnect}
        >
          <Form.Item
            name="api_key"
            label="API Key"
            rules={[{ required: true, message: 'Please enter your API key' }]}
          >
            <Input 
              prefix={<LockOutlined />} 
              placeholder="Enter API key"
            />
          </Form.Item>
          
          <Form.Item
            name="account_id"
            label="Account ID"
            rules={[{ required: true, message: 'Please enter your account ID' }]}
          >
            <Input 
              prefix={<UserOutlined />} 
              placeholder="Enter account ID"
            />
          </Form.Item>
          
          {selectedSystem?.requires_environment && (
            <Form.Item
              name="environment"
              label="Environment"
              rules={[{ required: true, message: 'Please select an environment' }]}
            >
              <Select placeholder="Select environment">
                <Option value="production">Production</Option>
                <Option value="sandbox">Sandbox</Option>
              </Select>
            </Form.Item>
          )}
          
          <Form.Item className="form-actions">
            <Button onClick={() => setConnectModalVisible(false)} style={{ marginRight: 8 }}>
              Cancel
            </Button>
            <Button type="primary" htmlType="submit" loading={loading}>
              Connect
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AccountingIntegration;
