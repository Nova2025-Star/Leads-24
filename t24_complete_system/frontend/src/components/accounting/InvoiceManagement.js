import React, { useState, useEffect } from 'react';
import { useAccounting } from '../../contexts/AccountingContext';
import { Row, Col, Button, Spin, Alert, Tag, Typography, Dropdown, Menu, Modal, Space } from 'antd';
import { 
  FileTextOutlined, 
  SyncOutlined,
  CheckCircleOutlined,
  DownloadOutlined,
  PrinterOutlined,
  MoreOutlined,
  ExportOutlined,
  FilterOutlined
} from "@ant-design/icons";
import ResponsiveCard from '../common/ResponsiveCard';
import ResponsiveTable from '../common/ResponsiveTable';
import { useMediaQuery } from 'react-responsive';
import './InvoiceManagement.css';

const { Text } = Typography;

const InvoiceManagement = ({ connectionId }) => {
  const { 
    invoices, 
    loading, 
    error, 
    fetchInvoices,
    createInvoiceFromQuote
  } = useAccounting();
  
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [quoteId, setQuoteId] = useState("");
  // const isMobile = useMediaQuery({ maxWidth: 576 });
  
  useEffect(() => {
    if (connectionId) {
      fetchInvoices(connectionId);
    }
  }, [fetchInvoices, connectionId]);
  
  const handleCreateInvoice = async () => {
    if (!quoteId || !connectionId) return;
    
    const result = await createInvoiceFromQuote(connectionId, quoteId);
    if (result) {
      setCreateModalVisible(false);
      setQuoteId('');
    }
  };
  
  const handleRefresh = () => {
    if (connectionId) {
      fetchInvoices(connectionId);
    }
  };
  
  // Get status tag color
  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'draft':
        return 'default';
      case 'sent':
        return 'processing';
      case 'paid':
        return 'success';
      case 'overdue':
        return 'error';
      case 'partial':
        return 'warning';
      default:
        return 'default';
    }
  };
  
  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };
  
  // Format currency
  const formatCurrency = (amount) => {
    return `$${parseFloat(amount).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };
  
  const columns = [
    {
      title: 'Invoice #',
      dataIndex: 'invoice_number',
      key: 'invoice_number',
      sorter: (a, b) => a.invoice_number.localeCompare(b.invoice_number)
    },
    {
      title: 'Customer',
      dataIndex: 'customer_name',
      key: 'customer_name',
      sorter: (a, b) => a.customer_name.localeCompare(b.customer_name)
    },
    {
      title: 'Date',
      dataIndex: 'invoice_date',
      key: 'invoice_date',
      render: (text) => formatDate(text),
      sorter: (a, b) => new Date(a.invoice_date) - new Date(b.invoice_date)
    },
    {
      title: 'Due Date',
      dataIndex: 'due_date',
      key: 'due_date',
      render: (text) => formatDate(text),
      sorter: (a, b) => new Date(a.due_date) - new Date(b.due_date),
      responsive: 'desktop-only'
    },
    {
      title: 'Amount',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (text) => formatCurrency(text),
      sorter: (a, b) => a.total_amount - b.total_amount
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (text) => (
        <Tag color={getStatusColor(text)}>
          {text.toUpperCase()}
        </Tag>
      ),
      sorter: (a, b) => a.status.localeCompare(b.status)
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Dropdown
          overlay={
            <Menu>
              <Menu.Item key="view" icon={<FileTextOutlined />}>
                View Details
              </Menu.Item>
              <Menu.Item key="download" icon={<DownloadOutlined />}>
                Download PDF
              </Menu.Item>
              <Menu.Item key="print" icon={<PrinterOutlined />}>
                Print
              </Menu.Item>
              <Menu.Divider />
              <Menu.Item key="mark-paid" icon={<CheckCircleOutlined />}>
                Mark as Paid
              </Menu.Item>
            </Menu>
          }
          trigger={['click']}
        >
          <Button type="text" icon={<MoreOutlined />} />
        </Dropdown>
      )
    }
  ];
  
  const rowSelection = {
    selectedRowKeys,
    onChange: (keys) => setSelectedRowKeys(keys),
  };
  
  if (loading && invoices.length === 0) {
    return (
      <div className="invoice-management-loading">
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
    <div className="invoice-management">
      <ResponsiveCard
        title="Invoice Management"
        icon={<FileTextOutlined />}
        className="invoice-card"
        headerExtra={
          <Space>
            <Button 
              type="primary" 
              onClick={() => setCreateModalVisible(true)}
            >
              Create Invoice
            </Button>
            <Button 
              icon={<SyncOutlined />} 
              onClick={handleRefresh}
            >
              Refresh
            </Button>
          </Space>
        }
      >
        <div className="invoice-actions">
          <div className="bulk-actions">
            <Text>
              {selectedRowKeys.length > 0 ? `${selectedRowKeys.length} invoices selected` : ''}
            </Text>
            {selectedRowKeys.length > 0 && (
              <Space>
                <Button icon={<DownloadOutlined />}>
                  Download Selected
                </Button>
                <Button icon={<ExportOutlined />}>
                  Export Selected
                </Button>
              </Space>
            )}
          </div>
          
          <div className="filter-actions">
            <Button icon={<FilterOutlined />}>
              Filter
            </Button>
          </div>
        </div>
        
        <ResponsiveTable
          columns={columns}
          dataSource={invoices}
          rowKey="id"
          rowSelection={rowSelection}
          pagination={{ pageSize: 10 }}
          searchable
          searchPlaceholder="Search invoices"
        />
        
        <div className="invoice-summary">
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={8}>
              <div className="summary-item">
                <Text>Total Invoices</Text>
                <Text strong>{invoices.length}</Text>
              </div>
            </Col>
            <Col xs={24} sm={8}>
              <div className="summary-item">
                <Text>Total Amount</Text>
                <Text strong className="amount">
                  {formatCurrency(invoices.reduce((sum, invoice) => sum + parseFloat(invoice.total_amount), 0))}
                </Text>
              </div>
            </Col>
            <Col xs={24} sm={8}>
              <div className="summary-item">
                <Text>Overdue</Text>
                <Text strong className="overdue">
                  {formatCurrency(invoices
                    .filter(invoice => invoice.status.toLowerCase() === 'overdue')
                    .reduce((sum, invoice) => sum + parseFloat(invoice.total_amount), 0)
                  )}
                </Text>
              </div>
            </Col>
          </Row>
        </div>
      </ResponsiveCard>
      
      {/* Create Invoice Modal */}
      <Modal
        title="Create Invoice from Quote"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        onOk={handleCreateInvoice}
        okText="Create Invoice"
        confirmLoading={loading}
      >
        <div className="create-invoice-form">
          <div className="form-item">
            <label>Quote ID</label>
            <input 
              type="text" 
              value={quoteId} 
              onChange={(e) => setQuoteId(e.target.value)} 
              placeholder="Enter quote ID"
            />
          </div>
          <div className="form-description">
            <Text type="secondary">
              This will create a new invoice in your accounting system based on the quote details.
            </Text>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default InvoiceManagement;
