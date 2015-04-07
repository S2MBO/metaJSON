//
//  _BaseJSONObject.m
//
//  Created by MetaJSONParser.
//  Copyright (c) 2014 SinnerSchrader Mobile. All rights reserved.

#import "APIParser.h"
#import "NSString+RegExValidation.h"
#import "BaseJSONObject.h"


@implementation _BaseJSONObject

#pragma mark - factory

+ (BaseJSONObject *)baseWithDictionary:(NSDictionary *)dic withError:(NSError **)error
{
    return [[BaseJSONObject alloc] initWithDictionary:dic withError:error];
}

#pragma mark - initialize
- (id)initWithDictionary:(NSDictionary *)dic  withError:(NSError **)error
{
    self = [super init];
    if (self) {
    }
    return self;
}

#pragma mark - getter

#pragma mark - NSCoding

- (void)encodeWithCoder:(NSCoder*)coder
{
    [super encodeWithCoder:coder];
}

- (id)initWithCoder:(NSCoder *)coder
{
    self = [super initWithCoder:coder];
    return self;
}

#pragma mark - Object Info
- (NSDictionary *)propertyDictionary
{
    NSMutableDictionary *dic = [[NSMutableDictionary alloc] init];
    return dic;
}

- (NSString *)description
{
    return [[self propertyDictionary] description];
}

@end
