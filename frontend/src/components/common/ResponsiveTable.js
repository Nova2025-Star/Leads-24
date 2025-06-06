import React from 'react';
import { useMediaQuery } from 'react-responsive';
import { Table, Empty, Spin, Input, Select } from 'antd';
import { SearchOutlined, FilterOutlined } from '@ant-design/icons';
import './ResponsiveTable.css';

const { Option } = Select;

const ResponsiveTable = ({
  columns,
  dataSource,
  loading = false,
  rowKey = 'id',
  pagination = true,
  onChange,
  searchable = false,
  searchPlaceholder = 'Search',
  onSearch,
  filterable = false,
  filterOptions = [],
  onFilter,
  emptyText = 'No data found',
  scroll,
  rowSelection,
  expandable,
  size,
  title,
  footer
}) => {
  // Media queries for responsive design
  const isMobile = useMediaQuery({ maxWidth: 576 });
  const isTablet = useMediaQuery({ minWidth: 577, maxWidth: 992 });
  
  // State for search and filter
  const [searchText, setSearchText] = React.useState('');
  const [filterValue, setFilterValue] = React.useState(undefined);
  
  // Handle search input change
  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchText(value);
    if (onSearch) {
      onSearch(value);
    }
  };
  
  // Handle filter select change
  const handleFilterChange = (value) => {
    setFilterValue(value);
    if (onFilter) {
      onFilter(value);
    }
  };
  
  // Adjust columns for responsive display
  const getResponsiveColumns = () => {
    if (!columns) return [];
    
    // On mobile, show only the most important columns (marked with responsive: true)
    if (isMobile) {
      return columns.filter(col => col.responsive !== false);
    }
    
    // On tablet, show medium priority columns
    if (isTablet) {
      return columns.filter(col => col.responsive !== 'desktop-only');
    }
    
    // On desktop, show all columns
    return columns;
  };
  
  // Adjust pagination for responsive display
  const getResponsivePagination = () => {
    if (!pagination) return false;
    
    const defaultPagination = {
      showSizeChanger: !isMobile,
      showQuickJumper: !isMobile,
      size: isMobile ? 'small' : 'default',
      pageSize: isMobile ? 5 : (isTablet ? 10 : 20),
      ...(typeof pagination === 'object' ? pagination : {})
    };
    
    return defaultPagination;
  };
  
  // Determine table size based on screen size
  const getTableSize = () => {
    if (size) return size;
    return isMobile ? 'small' : (isTablet ? 'middle' : 'default');
  };
  
  // Determine scroll configuration
  const getScrollConfig = () => {
    if (scroll) return scroll;
    
    return {
      x: isMobile ? 'max-content' : undefined,
      ...(!isMobile && { y: 400 })
    };
  };
  
  return (
    <div className="responsive-table-container">
      {/* Search and filter controls */}
      {(searchable || filterable) && (
        <div className="responsive-table-controls">
          {searchable && (
            <Input
              placeholder={searchPlaceholder}
              value={searchText}
              onChange={handleSearchChange}
              prefix={<SearchOutlined />}
              allowClear
              className="responsive-table-search"
            />
          )}
          
          {filterable && (
            <Select
              placeholder="Filter"
              value={filterValue}
              onChange={handleFilterChange}
              allowClear
              className="responsive-table-filter"
              suffixIcon={<FilterOutlined />}
            >
              {filterOptions.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          )}
        </div>
      )}
      
      {/* Table component */}
      <Table
        columns={getResponsiveColumns()}
        dataSource={dataSource}
        loading={{
          spinning: loading,
          indicator: <Spin />,
        }}
        rowKey={rowKey}
        pagination={getResponsivePagination()}
        onChange={onChange}
        locale={{
          emptyText: <Empty description={emptyText} />
        }}
        scroll={getScrollConfig()}
        rowSelection={rowSelection}
        expandable={expandable}
        size={getTableSize()}
        title={title}
        footer={footer}
        className={`responsive-table ${isMobile ? 'mobile' : ''} ${isTablet ? 'tablet' : ''}`}
      />
    </div>
  );
};

export default ResponsiveTable;
