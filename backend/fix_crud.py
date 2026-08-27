import os
import re

modules_dir = 'd:/projects/MH/MH_user_backend/backend/src/modules/'

for root, _, files in os.walk(modules_dir):
    if 'service.py' in files and 'schemas.py' in files:
        service_path = os.path.join(root, 'service.py')
        schemas_path = os.path.join(root, 'schemas.py')
        
        with open(service_path, 'r') as f:
            service_code = f.read()
            
        with open(schemas_path, 'r') as f:
            schemas_code = f.read()

        orig_service_code = service_code
        orig_schemas_code = schemas_code

        # 1. Replace object=data.model_dump() with object=data
        service_code = re.sub(r'object=data\.model_dump\(\)', r'object=data', service_code)
        
        # 2. Fix the dicts
        matches = list(re.finditer(r'crud_[a-z_]+\.create\([^)]*object=([a-zA-Z_]+)[^)]*\)', service_code))
        
        for m in matches:
            var_name = m.group(1)
            if var_name == 'data' or var_name.endswith('internal') or var_name == 'create_data':
                continue
            
            decl_match = re.search(fr'{var_name}\s*=\s*([a-zA-Z_]+)\.model_dump\(\)', service_code)
            if not decl_match:
                continue
                
            orig_data_var = decl_match.group(1)
            
            type_match = re.search(fr'{orig_data_var}\s*:\s*([a-zA-Z0-9_]+Create)', service_code)
            if not type_match:
                continue
                
            create_schema = type_match.group(1)
            internal_schema = f'{create_schema}Internal'
            
            assign_matches = list(re.finditer(fr'{var_name}\[\"([a-zA-Z_]+)\"\]\s*=\s*([a-zA-Z_]+)', orig_service_code))
            kwargs_list = [f'**{orig_data_var}.model_dump()']
            fields = []
            for am in assign_matches:
                kwargs_list.append(f'{am.group(1)}={am.group(2)}')
                fields.append(am.group(1))
                
            kwargs_str = ', '.join(kwargs_list)
            new_instantiation = f'{var_name} = {internal_schema}({kwargs_str})'
            
            service_code = re.sub(fr'{var_name}\s*=\s*{orig_data_var}\.model_dump\(\)', new_instantiation, service_code)
            service_code = re.sub(fr'{var_name}\[\"[a-zA-Z_]+\"\]\s*=\s*[a-zA-Z_]+\n\s*', '', service_code)
            
            if internal_schema not in schemas_code:
                internal_class = f'\n\nclass {internal_schema}({create_schema}):\n'
                for field in fields:
                    internal_class += f'    {field}: int\n'
                schemas_code += internal_class
                
            # Add to imports
            service_code = re.sub(fr'({create_schema})(?!Internal)', fr'\1, {internal_schema}', service_code, count=1)
            
        if service_code != orig_service_code:
            with open(service_path, 'w') as f:
                f.write(service_code)
            print(f'Updated {service_path}')
        if schemas_code != orig_schemas_code:
            with open(schemas_path, 'w') as f:
                f.write(schemas_code)
            print(f'Updated {schemas_path}')
