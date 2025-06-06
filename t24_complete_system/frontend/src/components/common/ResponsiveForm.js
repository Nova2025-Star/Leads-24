import React from 'react';
import { useMediaQuery } from 'react-responsive';
import { Form, Input, Select, DatePicker, Button, Upload, Switch, Radio, Checkbox, InputNumber } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import './ResponsiveForm.css';

const { Option } = Select;
const { RangePicker } = DatePicker;
const { TextArea } = Input;

const ResponsiveForm = ({
  form,
  layout = 'vertical',
  initialValues = {},
  onFinish,
  onFinishFailed,
  fields = [],
  submitText = 'Submit',
  resetText = 'Reset',
  loading = false,
  showReset = true,
  className = '',
  disabled = false
}) => {
  // Media queries for responsive design
  const isMobile = useMediaQuery({ maxWidth: 576 });
  const isTablet = useMediaQuery({ minWidth: 577, maxWidth: 992 });
  
  // Determine column span based on screen size and field configuration
  const getColSpan = (field) => {
    const defaultSpan = field.span || 24;
    
    if (isMobile) {
      return 24; // Full width on mobile
    } else if (isTablet) {
      return field.tabletSpan || (defaultSpan <= 12 ? 12 : 24); // Half width or full width on tablet
    } else {
      return defaultSpan; // Original span on desktop
    }
  };
  
  // Reset form fields
  const handleReset = () => {
    form.resetFields();
  };
  
  // Render form field based on type
  const renderFormField = (field) => {
    const {
      name,
      label,
      type = 'input',
      placeholder,
      rules = [],
      options = [],
      disabled: fieldDisabled = false,
      ...restProps
    } = field;
    
    // Common props for all field types
    const commonProps = {
      placeholder,
      disabled: disabled || fieldDisabled,
      ...restProps
    };
    
    // Render different field types
    switch (type) {
      case 'input':
        return <Input {...commonProps} />;
        
      case 'textarea':
        return <TextArea rows={4} {...commonProps} />;
        
      case 'number':
        return <InputNumber style={{ width: '100%' }} {...commonProps} />;
        
      case 'select':
        return (
          <Select {...commonProps}>
            {options.map(option => (
              <Option key={option.value} value={option.value}>
                {option.label}
              </Option>
            ))}
          </Select>
        );
        
      case 'date':
        return <DatePicker style={{ width: '100%' }} {...commonProps} />;
        
      case 'dateRange':
        return <RangePicker style={{ width: '100%' }} {...commonProps} />;
        
      case 'switch':
        return <Switch {...commonProps} />;
        
      case 'radio':
        return (
          <Radio.Group {...commonProps}>
            {options.map(option => (
              <Radio key={option.value} value={option.value}>
                {option.label}
              </Radio>
            ))}
          </Radio.Group>
        );
        
      case 'checkbox':
        return <Checkbox {...commonProps}>{field.checkboxLabel}</Checkbox>;
        
      case 'upload':
        return (
          <Upload {...commonProps}>
            <Button icon={<UploadOutlined />}>{field.buttonText || 'Upload'}</Button>
          </Upload>
        );
        
      default:
        return <Input {...commonProps} />;
    }
  };
  
  return (
    <Form
      form={form}
      layout={layout}
      initialValues={initialValues}
      onFinish={onFinish}
      onFinishFailed={onFinishFailed}
      className={`responsive-form ${className} ${isMobile ? 'mobile' : ''} ${isTablet ? 'tablet' : ''}`}
    >
      <div className="responsive-form-fields">
        {fields.map((field, index) => (
          <div 
            key={field.name || index} 
            className="responsive-form-field"
            style={{ width: `${(getColSpan(field) / 24) * 100}%` }}
          >
            <Form.Item
              name={field.name}
              label={field.label}
              rules={field.rules}
              valuePropName={field.type === 'switch' || field.type === 'checkbox' ? 'checked' : 'value'}
              className={field.className}
            >
              {renderFormField(field)}
            </Form.Item>
          </div>
        ))}
      </div>
      
      <Form.Item className="responsive-form-buttons">
        <Button
          type="primary"
          htmlType="submit"
          loading={loading}
          disabled={disabled}
        >
          {submitText}
        </Button>
        
        {showReset && (
          <Button 
            htmlType="button" 
            onClick={handleReset}
            disabled={disabled}
            className="reset-button"
          >
            {resetText}
          </Button>
        )}
      </Form.Item>
    </Form>
  );
};

export default ResponsiveForm;
