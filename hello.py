import { useReducer, useEffect } from 'react';
function selectFieldPattern(type: string, priorityPattern?: RegExp): RegExp {
  if (priorityPattern) {
    return priorityPattern;
  }
  switch (type.toUpperCase()) {
    case 'ANY':
      return /^.*$/;
    case 'TEXT':
      return /^[a-zA-Z ]+$/;
    case 'TEXTAREA':
      return /^[a-zA-Z\s\.]+$/;
    case 'EMAIL':
      return /^[\.0-9A-Za-z]+@[\.0-9A-Za-z]+$/;
    case 'PASSWORD':
      return /.{8,}/;
    case 'NUMBER':
      return /^[0-9]+$/;
    case 'PHONE':
      return /^[0-9]{12,14}$/;
    case 'FILE':
      return selectFieldPattern('ANY');
    default:
      return selectFieldPattern('ANY');
  }
}
interface BaseFieldType {
  type: string;
  pattern?: RegExp;
}
interface RawFieldType extends BaseFieldType {}
interface RealFieldType extends BaseFieldType {
  isValid: boolean;
  value: string;
}
interface RealFieldsType {
  [name: string]: RealFieldType;
}
interface OutputFieldsType {
  [name: string]: {
    isValid: boolean;
    value: string;
  };
}
interface FormProps {
  isValid: boolean;
  fields: RealFieldsType;
}
enum FormActionTypes {
  Update = 1,
  Validate = 2,
}
type ActionType =
  | {
    type: FormActionTypes.Update;
    field: {
      name: string;
      value: string;
    };
  }
  | {
    type: FormActionTypes.Validate;
  };
function validateForm(fields: RealFieldsType): boolean {
  return Object.keys(fields).reduce((isValid: boolean, fieldName: string) => {
    return isValid && fields[fieldName].isValid;
  }, true);
}
function formManipulator(form: FormProps, action: ActionType) {
  const newForm = { ...form };
  switch (action.type) {
    case FormActionTypes.Update: {
      if (!newForm.fields[action.field.name]) {
        throw new Error("The field name doesn't exist");
      }
      const { type } = newForm.fields[action.field.name];
      const priorityPattern = newForm.fields[action.field.name].pattern;
      const fieldValue = typeof action.field.value === 'string'
        ? action.field.value.trim()
        : action.field.value;
      newForm.fields[action.field.name].value = fieldValue;
      newForm.fields[action.field.name].isValid = selectFieldPattern(
        type,
        priorityPattern
      ).test(fieldValue);
      newForm.isValid = validateForm(newForm.fields);
      break;
    }
    case FormActionTypes.Validate: {
      newForm.isValid = validateForm(newForm.fields);
      break;
    }
    default:
      return newForm;
  }
  return newForm;
}
interface FieldsInObjectType {
  [name: string]: RawFieldType;
}
interface OutputFormType {
  isValid: boolean;
  fields: OutputFieldsType;
}
type OutputSetterType = (name: string, value: string) => void;
export default function useFormState(
  fields: FieldsInObjectType
): [OutputFormType, OutputSetterType] {
  const [form, dispatchForm] = useReducer(formManipulator, {
    isValid: false,
    fields: Object.keys(fields).reduce(
      (oldFields: RealFieldsType, fieldName: string) => {
        const newFields: RealFieldsType = { ...oldFields };
        const value = '';
        newFields[fieldName] = {
          ...fields[fieldName],
          isValid: selectFieldPattern(fields[fieldName].type).test(value),
          value,
        };
        return newFields;
      },
      {}
    ),
  });
  // Validate a single form after validate each field
  useEffect(() => {
    dispatchForm({ type: FormActionTypes.Validate });
  }, []);
  // Filtering the form before showing to end-user
  const returnedForm = { ...form };
  returnedForm.fields = Object.keys(returnedForm.fields).reduce(
    (oldFields, fieldName) => {
      const newFields: OutputFieldsType = { ...oldFields };
      newFields[fieldName] = {
        value: returnedForm.fields[fieldName].value,
        isValid: returnedForm.fields[fieldName].isValid,
      };
      return newFields;
    },
    {}
  );
  const setField = (name: string, value: string) => {
    dispatchForm({ type: FormActionTypes.Update, field: { name, value } });
  };
  return [returnedForm, setField];
}
