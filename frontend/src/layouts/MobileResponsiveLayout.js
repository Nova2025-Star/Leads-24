import React from 'react';
import { useMediaQuery } from 'react-responsive';
import { Layout, Menu, Button, Drawer } from 'antd';
import { MenuOutlined } from '@ant-design/icons';
import NotificationCenter from '../components/notifications/NotificationCenter';
import './MobileResponsiveLayout.css';

const { Header, Sider, Content } = Layout;

const MobileResponsiveLayout = ({ 
  children, 
  menuItems, 
  selectedKey, 
  onMenuSelect, 
  logo, 
  title 
}) => {
  const [drawerVisible, setDrawerVisible] = React.useState(false);
  
  // Media queries for responsive design
  const isMobile = useMediaQuery({ maxWidth: 768 });
  const isTablet = useMediaQuery({ minWidth: 769, maxWidth: 1024 });
  
  const showDrawer = () => {
    setDrawerVisible(true);
  };
  
  const closeDrawer = () => {
    setDrawerVisible(false);
  };
  
  // Handle menu selection and close drawer on mobile
  const handleMenuSelect = (item) => {
    if (isMobile) {
      closeDrawer();
    }
    onMenuSelect(item);
  };
  
  return (
    <Layout className="mobile-responsive-layout">
      {/* Sidebar - shown on desktop, hidden on mobile */}
      {!isMobile && (
        <Sider
          width={isTablet ? 200 : 250}
          className="mobile-responsive-sider"
          breakpoint="lg"
          collapsedWidth="0"
        >
          <div className="logo">
            {logo}
            {!isTablet && <h2>{title}</h2>}
          </div>
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[selectedKey]}
            items={menuItems}
            onClick={handleMenuSelect}
          />
        </Sider>
      )}
      
      <Layout>
        {/* Header - always visible */}
        <Header className="mobile-responsive-header">
          {/* Mobile menu button */}
          {isMobile && (
            <Button
              className="mobile-menu-button"
              type="text"
              icon={<MenuOutlined />}
              onClick={showDrawer}
            />
          )}
          
          {/* Title in header on mobile */}
          {isMobile && (
            <div className="mobile-header-title">
              {logo}
              <h2>{title}</h2>
            </div>
          )}
          
          {/* Notification center */}
          <div className="header-right">
            <NotificationCenter />
          </div>
        </Header>
        
        {/* Main content */}
        <Content className="mobile-responsive-content">
          {children}
        </Content>
      </Layout>
      
      {/* Mobile drawer menu */}
      {isMobile && (
        <Drawer
          title={title}
          placement="left"
          onClose={closeDrawer}
          open={drawerVisible}
          bodyStyle={{ padding: 0 }}
        >
          <Menu
            theme="light"
            mode="inline"
            selectedKeys={[selectedKey]}
            items={menuItems}
            onClick={handleMenuSelect}
          />
        </Drawer>
      )}
    </Layout>
  );
};

export default MobileResponsiveLayout;
